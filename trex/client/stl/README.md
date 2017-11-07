#### services
Contains TRex stateless client dependencies provided by TRex developers


#### trex_stl_lib
Contains TRex stateless client code provided by TRex developers

*test_common.py*

* inits TRex server with _trex_test_init.py_
* starts test with _trex_test_proc.py_
* cancels server reservation with _../stf/trex_reservation.py_
* returns result of test

*test_selection.py*

* inits TRex server with _trex_test_init.py_
* runs test series with given settings using _trex_test_proc.py_
* cancels server reservation with _../stf/trex_reservation.py_
* gathers and returns test result if one passes criterion which was defined in test settings

*trex_test_init.py*

* inits TRex server with _../stf/trex_test_init.py_
* starts TRex server in stateless mode

*trex_test_proc.py*

* connects to TRex server with TRex client
* runs given test
* gathers and returns test result
