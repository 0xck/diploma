#### client
Contains code for TRex client handling

#### test
Contains data for tests that are used by TRex

##### *test_handler.py*

* sends given data to TRex using appropriate test type
* returns test data result

##### *test_proc.py*

* takes given task
* gather test settings from DB
* sets statuses of TRex and device
* sends one to [test_handler](#test_handler)
* receives data and writes one to DB
* restores statuses of TRex and device
