#### services
Contains TRex stateless client dependencies provided by TRex developers


#### trex_stl_lib
Contains TRex stateless client code provided by TRex developers

##### test_common.py

* inits TRex server with [trex_test_init.py](#trex_test_initpy)
* starts test with [trex_test_proc.py](#trex_test_procpy)
* cancels server reservation with [../stf/trex_reservation.py](https://github.com/0xck/wrex/tree/dev/trex/client/stf#trex_reservationpy)
* returns result of test

##### test_selection.py

* inits TRex server with [trex_test_init.py](#trex_test_initpy)
* runs test series with given settings using [trex_test_proc.py](#trex_test_procpy)
* cancels server reservation with [../stf/trex_reservation.py](https://github.com/0xck/wrex/tree/dev/trex/client/stf#trex_reservationpy)
* gathers and returns test result if one passes criterion which was defined in test settings

##### trex_test_init.py

* inits TRex server with [../stf/trex_test_init.py](https://github.com/0xck/wrex/tree/dev/trex/client/stf#trex_test_initpy)
* starts TRex server in stateless mode

##### trex_test_proc.py

* connects to TRex server with TRex client
* runs given test
* gathers and returns test result
