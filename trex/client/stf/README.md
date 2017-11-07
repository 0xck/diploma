#### trex_stf_lib
Contains TRex stateful client code provided by TRex developers

*test_common.py*

* inits TRex server with _trex_test_init.py_
* starts test with _trex_test_proc.py_
* cancels server reservation with _trex_reservation.py_
* returns result of test

*test_selection.py*

* runs test series with given settings using _trex_test_proc.py_
* cancels server reservation with _trex_reservation.py_
* gathers and returns test result if one passes criterion which was defined in test settings

*trex_kill.py*

* kills current TRex server task by _soft_ or _force_ methods

*trex_reservation.py*

* returns TRex reservation state

*trex_status.py*

* returns TRex server state

*trex_test_init.py*

* checks TRex server status with _trex_status.py_
    - tries to release in case not _idle_ state with _trex_kill.py_
* checks TRex server reservation with _trex_reservation.py_
    - tries to release reservation in case server is reserved
    - tries to reserve server for given user

*trex_test_proc.py*

* connects to TRex server with TRex client
* runs given test
* gathers and returns test result
