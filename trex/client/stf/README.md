#### trex_stf_lib
Contains TRex stateful client code provided by TRex developers

##### test_common.py

* inits TRex server with [trex_test_init.py](#trex_test_initpy)
* starts test with [trex_test_proc.py](#trex_test_procpy)
* cancels server reservation with [trex_reservation.py](#trex_reservationpy)
* returns result of test

##### test_selection.py

* runs test series with given settings using [trex_test_proc.py](#trex_test_procpy)
* cancels server reservation with [trex_reservation.py](#trex_reservationpy)
* gathers and returns test result if one passes criterion which was defined in test settings

##### trex_kill.py

* kills current TRex server task by _soft_ or _force_ methods

##### trex_reservation.py

* returns TRex reservation state

##### trex_status.py

* returns TRex server state

##### trex_test_init.py

* checks TRex server status with [trex_status.py](#trex_statuspy)
    - tries to release in case not _idle_ state with [trex_kill.py](#trex_killpy)
* checks TRex server reservation with [trex_reservation.py](#trex_reservationpy)
    - tries to release reservation in case server is reserved
    - tries to reserve server for given user

##### trex_test_proc.py

* connects to TRex server with TRex client
* runs given test
* gathers and returns test result
