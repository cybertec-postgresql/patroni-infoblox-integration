Patroni Infoblox DNS integration
================================

This software enables the setup of a master database service DNS entry in Infoblox network services for databases
managed by Patroni. The hostname will be redirected to the current master any time a failover or switchover happens.

Installation
------------

The package can be installed with Python's pip package manager: 
 
    pip install .

Only external dependency is on `infoblox-client`, the official Python client provided by Infoblox.

Setup
-----
 
Make sure when Patroni is started with the following environment variables set. When using SystemD to start Patroni
a good place to set them would be from an `EnvironmentFile` referenced from the SystemD `patroni.service` used to 
start Patroni.

    WAPI_HOSTNAME="10.2.3.4" # Address where WAPI REST services can be accessed
    WAPI_USER="foo"          # User to authenticate to WAPI with
    WAPI_PASSWORD="bar"      # Password for authentication
    # Template for hostname. {cluster} will get replaced by cluster name from Patroni (scope)
    DATABASE_MASTER_HOSTNAME_TEMPLATE="master.{cluster}.dbs.example.com"
    

In Patroni configuration add the following lines to enable the callback to be called.

    postgresql:
        callbacks:
            on_restart: infoblox-callback.py 
            on_role_change: infoblox-callback.py
            on_start: infoblox-callback.py
            on_stop: infoblox-callback.py

If using environment variables is not desired for some reason, the parameters can also be passed through Patroni
configuration file:

    postgresql:
        callbacks:
            on_restart: infoblox-callback.py -H 10.2.3.4 -u foo -p bar -4 master.{cluster}.dbs.example.com 
            on_role_change: infoblox-callback.py -H 10.2.3.4 -u foo -p bar -4 master.{cluster}.dbs.example.com
            on_start: infoblox-callback.py -H 10.2.3.4 -u foo -p bar -4 master.{cluster}.dbs.example.com
            on_stop: infoblox-callback.py -H 10.2.3.4 -u foo -p bar -4 master.{cluster}.dbs.example.com

This config will create and/or update an ARecord in DNS view called `default`. If a different DNS view needs to be
 used it can be specified with WAPI_DNS_VIEW.
 
Options
-------

| Environment variable                | Command line parameter | Required | Description |
|-------------------------------------|------------------------|:--------:|-------------|
| `DATABASE_MASTER_HOSTNAME_TEMPLATE` | `-4` `--arecord`       | Y        | Hostname to create. A `{cluster}` placeholder will be replaced with cluster name (scope) from Patroni. | 
|                                     | `-i` `--ip`            | N        | IP address that the hostname should point to when this host is master. Default is automatically detected from network interfaces. |
| `WAPI_HOST`                         | `-H` `--host`          | Y        | WAPI REST API endpoint hostname or IP |
| `WAPI_USER`                         | `-u` `--username`      | Y        | WAPI username for authentication |
| `WAPI_PASSWORD`                     | `-p` `--password`      | Y        | WAPI password for authentication |
| `WAPI_DNS_VIEW`                     | `-v` `--dns-view`      | N        | WAPI DNS view where the hostname is created |
| `WAPI_COMMENT`                      | `--comment`            | N        | Comment to set on the created hostname. `{cluster}` will be replaces with cluster name (scope) from Patroni. |
| `WAPI_VERSION`                      | `--wapi-version`       | N        | WAPI API version to access. |
|                                     | `--debug`              | N        | Extra logging for debugging |

