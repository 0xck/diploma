Contains some code for TRex client and server

#### client
Contains code for TRex client handling

#### conf
Contains examples of TRex server config

#### test
Contains data for tests that are used by TRex (traffic profiles, etc)

##### test_handler.py

* sends given data to TRex using appropriate test type
* returns test data result

##### test_proc.py

* takes given task
* gathers test settings from DB
* sets statuses of TRex and device
* sends data to [test_handler](#test_handler)
* receives data and writes one to DB
* restores statuses of TRex and device
