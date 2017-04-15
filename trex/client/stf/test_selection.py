from . import trex_test_proc, trex_test_init, trex_reservation


class Criterion():
    # criterion for testing cycle
    def __init__(self, accuracy=0.001, rate=1, rate_incr_step=1, max_succ_attempt=3, max_test_count=30, **kwargs):
        # traffic rate: multiplier
        self.rate = rate
        # test accuracy in packets loss which is not more 1/number of %, e.g. 0.001 means 0.1%
        self.accuracy = accuracy
        # rate increase step
        self.rate_incr_step = rate_incr_step
        # number of maximum success attempts for calling rate valid
        self.max_succ_attempt = max_succ_attempt
        # test counter, maximum number of tests in order to escape test loop
        self.max_test_count = max_test_count
        # number success attempts of test with safa value rate
        self.succ_attempt = 0
        # safe value test switch
        self.safe_value_test = False
        # test count
        self.test_count = 0
        # safe value that means rate might be appropriate to criterion drops and losses
        self.safe_value = 0

    def test_count_incr(self):
        # increases test count
        self.test_count += 1

    def safe_value_change(self):
        # changes safe value to current rate
        self.safe_value = self.rate

    def safe_value_decr(self):
        # decreases safe value on rate increase step
        self.safe_value -= self.rate_incr_step

    def succ_attempt_incr(self):
        # increases success attempts count
        self.succ_attempt += 1

    def rate_incr(self):
        # increases rate on rate increase step
        self.rate += self.rate_incr_step

    def rate_decr(self):
        # decreases rate on rate increase step
        self.rate -= self.rate_incr_step


def processing(task, **kwargs):

    def testing(**kwargs):
        # func for making test
        # trying to make a test
        result = trex_test_proc.test(**kwargs)
        return result

    # result template
    result = {'status': True, 'state': ''}
    # making initial checking
    trex_init = trex_test_init.initialize(**kwargs)
    # checkig if trex daemon is ready to make test
    if trex_init['state'] == 'idle':
        # changing multiplier to rate
        kwargs['multiplier'] = task.rate
        # 1st test
        test = testing(**kwargs)
        # no problem with 1st test

        print('\n1st', test, '\n')

        if test['status']:
            # statrs cycle of testing in order to find appropriate rate
            while test['status'] and task.test_count < task.max_test_count and task.succ_attempt < (task.max_succ_attempt + 1) and task.rate > 0:
                # getting values for comparison
                tx_p_0 = test['values']['global']['tx_ptks']['opackets-0']
                rx_p_1 = test['values']['global']['rx_ptks']['ipackets-1']
                tx_p_1 = test['values']['global']['tx_ptks']['opackets-1']
                rx_p_0 = test['values']['global']['rx_ptks']['ipackets-0']
                drop = False
                for drop_count in test['values']['sampler']:
                    if drop_count['queue_drop'] > 0:
                        drop = True
                        break
                # cheking condition
                if (tx_p_0 - rx_p_1 < tx_p_0 * task.accuracy) and (tx_p_1 - rx_p_0 < tx_p_1 * task.accuracy) and not drop:
                    # no drops, losses are in valid limits
                    # test is not safe value test
                    if not task.safe_value_test:
                        # increases safe value
                        task.safe_value_change()
                        # increases rate
                        task.rate_incr()
                    # safe value test
                    else:
                        # increases safe value test count
                        task.succ_attempt_incr()
                # drops or losses are not in valid limits
                else:
                    # safe value is not defined yet
                    if task.safe_value == 0:
                        # decreases rate
                        task.rate_decr()
                    # fail after successfull tests
                    elif not task.safe_value_test:
                        # sets rate from safe value
                        task.rate = task.safe_value
                        # enabling safe value test
                        task.safe_value_test = True
                    # fail during safe value test
                    else:
                        # decreases safe value
                        task.safe_value_decr()
                        # sets rate from safe value
                        task.rate = task.safe_value
                        # sets safe value success test attempt to 0 for new cycle of test
                        task.succ_attempt = 0
                # increases test count
                task.test_count_incr()
                # changing multiplier to rate
                kwargs['multiplier'] = task.rate
                # making new test
                test = testing(**kwargs)

                print('\n#{}\n{}'.format(task.test_count, test))

            # after cycle of tests checking conditions
            # tests were complited due max count exceed
            if task.test_count >= task.max_test_count:
                result['status'] = False
                result['state'] = 'max count was exceeded'
            # rate was decreased to 0 or less
            elif task.rate <= 0:
                result['status'] = False
                result['state'] = 'rate is equal or less than 0'
            # something happened during test
            elif not test['status']:
                result = test
            # appropriate rate was found
            else:
                result = test
                # adding rate value to result
                result['rate'] = task.rate
        # something happened during 1st test
        else:
            result = test
        # trying to cancel reservation after test, return nothing
        try:
            if isinstance(result['state'], dict) or result['state'] not in {'other_user', 'running', 'error_rpc'}:
                trex_reservation.cancel(**kwargs)
        except KeyError:
            pass
    # something wrong with trex daemon
    else:
        result = trex_init

    return result


'''
if __name__ == '__main__':
    task = Criterion(rate=1000, rate_incr_step=1000, max_succ_attempt=2, max_test_count=30)
    kwargs = dict(trex_mng='172.16.150.23', duration=35, warm=5, multiplier=100, sampler=10, daemon_port=8090)
    a = processing(task=task, **kwargs)
    print(a)
'''
