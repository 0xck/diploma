# wrex
Small app for network device testing with [Cisco T-rex](https://trex-tgn.cisco.com)
> App is still in active development state now and some features mignt not work or work improperly

## Requirements
App writes on _python_ and needs *python 3* _(3.5 and above would be better)_. And you should install several *python modules* from requirements.txt _(see install notes below)._
App _works on *NIX_ systems _(due some Windows limitations, see limits below)._
*Redis* server is required, because some elemets using queue feature. You may _install new_ or _use existing_ redis server.
*Cisco T-rex* installed locally or separately

## Install
#### Python
Make sure you have got installed _python 3_, if not just using system software manager _(e.g. apt, yum, pkg)_ or download one from [official site](https://www.python.org/downloads/) and install. App tested on 3.5 version and should work on other python 3 releases as well.

#### Python modules
Install all python modules listed in _requirements.txt:_
- Flask
- Flask-SQLAlchemy
- Flask-Script
- Flask-WTF
- rq
- timeout-decorator
For this purpose you may do it using any module manager: _pip, easyinstall, pypm._ Below for example pip manager is used. module `pip` if one is not installed on yuor system just install one using software manager _(e.g. apt, yum, pkg)._ And go to app directory and execute command:
`python3 -m pip install -r requirements.txt` or if your system uses python3 by default `pip install -r requirements.txt`
*Note.* _Some systems do not allow you install modules using module manager in that case you have several ways: using sudo/root or install modules with system software manager._
_Actually there is one more way using virtual python environment, but it makes additional complication in using app and that is the reason I do not recomend this way for people who do not what is it and how do use one._

#### Redis server

