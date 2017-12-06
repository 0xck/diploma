# wrex
Small python wrapper on [Cisco TRex](https://trex-tgn.cisco.com) python API which makes testing easier
> App is still in active development state now and some features might not work or work improperly

## Table of Contents
[Requirements](#requirements)

[Install](#install)
- [Python](#python)
- [Cisco TRex](#cisco-trex)
    - [Setup and configuration](#setup-and-configuration)
    - [Daemon operations](#daemon-operations)

[Limits](#limits)
- [Operation system limits](#operation-system-limits)
- [TRex limits](#trex-limits)
    - [Open issues](#open-issues)

## Requirements
App is written on _python_ and needs **python 3** _(3.6 and above would be better)_. And you should install several **python modules** from requirements.txt _(see [Install](#install) notes below)._

**Cisco TRex** installed locally or separately

## Install
Download last [app release](https://github.com/0xck/wrex/releases) and unarchive into directory you plan to use for app.

### Python
Make sure you have got installed _python 3_, otherwise just use system software manager _(e.g. apt, yum, pkg)_ or download one from [official site](https://www.python.org/downloads/) and install. App tested on 3.5 version and should work on other python 3 releases as well.

### Cisco TRex
>Cisco TRex is used as main network testing software.

###### Setup and configuration
This product is available in [repository](http://trex-tgn.cisco.com/trex/release/). Download latest release and setup it using [official documentation](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_first_time_running). One may be installed on several Linux distro (please check capability [here](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_supported_versions)) as bare-metal or [VM instance](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_trex_on_esxi). Please check [hardware recomendations](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_hardware_recommendations) in order to make sure TRex will function properly.

---
**Note.** You may install TRex on the same host there app is installed.

For example a couple TRex config:

TRex config for _2x1G interfaces and L3:_
```yaml
- port_limit      : 2
  version         : 2
  interfaces      : ["03:00.0","0b:00.0"]
  port_bandwidth_gb : 1
  port_info       :
          - ip         : 192.168.1.10
            default_gw : 192.168.1.1
          - ip         : 10.0.1.10
            default_gw : 10.0.1.1
```

TRex config for _2x10G interfaces L2:_
```yaml
- port_limit      : 2
  version         : 2
  interfaces      : ["03:00.0","0b:00.0"]
  port_bandwidth_gb : 10
  port_info       :
          - dest_mac        :   [0x0,0x0,0x0,0x2,0x0,0x0]
            src_mac         :   [0x0,0x0,0x0,0x1,0x0,0x0]
          - dest_mac        :   [0x0,0x0,0x0,0x4,0x0,0x0]
            src_mac         :   [0x0,0x0,0x0,0x3,0x0,0x0]
```

---
**Attention.** Item `interfaces` has to contain list of proper NICs ID use `dpdk_setup_ports.py -s` with sudo/root privileges for finding your values, see [manual](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_identify_the_ports).

Item `port_info ` must be changed on your values.
###### Daemon operations
After TRex setup was completed, go to TRex directory and start a daemon `trex_daemon_server start` with sudo/root privileges. Also you can check status `trex_daemon_server show`, restat `trex_daemon_server restart` and stop daemon `trex_daemon_server stop`, use sudo/root privileges for all of them.

---
**Note.** By default daemon listens _TCP port 8090_ make sure this port is available for wrex host. Also for stateless TRex mode _TCP ports 4500 and 4501_ have to be available for wrex host. More about stateful/stateless modes see at [documentation](https://trex-tgn.cisco.com/trex/doc/trex_stateless.html#_stateful_vs_stateless).

## Limits
>There are some limits for using app in whole. They are described below.

#### Operation system limits
App works only on *NIX systems:
- some app components _(RQ workers)_ use `fork()` that is not implemented on Windows
- app contains TRex client which works with certain libraries that are able to work only on *NIX
- app works on 64bit systems only _(looks like something wrong with TRex client pyzmq python module from "external lib")_

#### TRex limits
Current TRex releases have some limits _(got from [here](https://communities.cisco.com/community/developer/trex/blog/2017/03/29/how-trex-is-used-by-mellanox))_:

TRex Missing Functionality:

The following items are lacking from TRex in our view:
1. TCP Stack
2. Simulation of packet loss and simulation of retransmission handling.
3. Routing Emulation Support - BGP/OSPF/ARP/VRRP/DHCP/PIM
4. Stateless GUI Gaps:
    - Build/send L2/L3 frames of control protocols, such as STP/LACP/OSPF/BGP.
    - L2 protocol emulation (LACP, STP and IGMP) support.
    - Incremental support on the following fields - VLAN/PRI/TCP Port Number/MTU.
    - Capture capabilities

Also one has [hardware](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_hardware_recommendations) and [software](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_hardware_recommendations) limits.

###### Open issues
You can acquaint them [here](https://trex-tgn.cisco.com/youtrack/issues/).
