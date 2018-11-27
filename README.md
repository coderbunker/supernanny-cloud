# Introduction
The following will explain how to install and configure the TICK stack used by Super Nanny.

If you need a server, spin up one at digitalocean or equivalent.

It is currently aimed at CentOS. If you want to do this on Ubuntu/Debian instead, please document and add your instructions to this README.

# Install and Configure TICK Droplet
## Update the system
```bash
yum makecache fast && yum update -y && yum upgrade -y
```
## Install Default Tools
```bash
yum install yum-utils vim firewalld policycoreutils-python bash-completion bash-completion-extras wget
```

## Enable FirewallD for better security
```
systemctl enable firewalld
systemctl start firewalld
```

## Install Nginx Proxy
### Add nginx repository
> NOTE: The enabled flag is set to 0 to disable the repository.
   The reason for that is to prevent auto update of the influxdb if the os gets patched/updated by yum update/upgrade.
   To install/update the influxdb packages the --enablerepo=nginx flag needs to be used
```
cat <<EOF | sudo tee /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/\$releasever/\$basearch/
gpgcheck=0
enabled=0
EOF
```

### Install, start und enable nginx proxy
```
yum install nginx --enablerepo=nginx
systemctl enable nginx
systemctl start nginx
```
### Install certbot to get free letsencrypt ssl certs
```
yum install epel-release
yum-config-manager --disable epel
yum install python2-certbot-nginx --enablerepo=epel
```

### Reload the firewall and enable the service permanent
```
firewall-cmd --reload
firewall-cmd --add-service=http --zone=public --permanent
firewall-cmd --add-service=https --zone=public --permanent
firewall-cmd --reload
```





## Install InfluxDB
### Add InfluxDB Repository
> NOTE: The enabled flag is set to 0 to disable the repository.
   The reason for that is to prevent auto update of the influxdb if the os gets patched/updated by yum update/upgrade.
   To install/update the influxdb packages the --enablerepo=influxdb flag needs to be used
```
cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 0
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF
```
### Install InfluxDB package
```
yum install influxdb --enablerepo=influxdb
```
### Start and Enable influxdb
```
systemctl start influxdb
systemctl enable influxdb
```
### Create firewalld service
```
# If you dont know how to use vi, try switching it out to nano
vi /etc/firewalld/services/coderbunker-influxdb.xml
```
```
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>CoderBunker-InfluxDB</short>
  <description>CoderBunker InfluxDB for the Super Nanny Project</description>
  <port protocol="tcp" port="8086"/>
</service>
```
### Reload the firewall and enable the service permanent
```
firewall-cmd --reload
firewall-cmd --add-service=coderbunker-influxdb --zone=public --permanent
firewall-cmd --reload
```

## Configure InfluxDB
### Setup Databases
Enter Influxdb shell
```bash
    influx
```
Add the following
```
    CREATE DATABASE "energy-monitor"
    CREATE DATABASE "telegraf"
    CREATE DATABASE "air-quality"
```

### Adding users
We need the following users with the following permissions:
 - chronograf - admin
 - telegraf - telegraf(WRITE)
 - energy-monitor - energy-monitor(WRITE)
 - air-quality - air-quality(WRITE)
 - grafana - all(READ)

PW's are stored in the spreadsheet.

Enter Influxdb shell
```bash
    influx
```

Creating admin user:
```
CREATE USER "<USER>" WITH PASSWORD '<PASSWORD>' WITH ALL PRIVILEGES
```

Creating non-admin user:
```
CREATE USER "<USER>" WITH PASSWORD '<PASSWORD>'
GRANT [READ,WRITE,ALL] ON <database_name> TO <username>
```
More at: https://docs.influxdata.com/influxdb/v1.6/administration/authentication_and_authorization/

### Configure for access
Find your influxdb config file:
```bash
    find / -name "influxdb.conf"
```
Open it and search for "http".
Add the following lines (or just un-comment and edit the examples) to enable:
```
    enabled = true
    bind-address = ":8086"
    auth-enabled = true
```
Then restart influxd:
```bash
    systemctl restart influxdb.service
```
To test this is all now working, from your pi (not the server) run:
```bash
    curl -G http://YOURSERVERIP:8086/query -u chronograf:PASSWORD --data-urlencode "q=SHOW DATABASES"
```

## Install Chronograf

### Install Chronograf package
```
yum install chronograf --enablerepo=influxdb
```
### Start and Enable Chronograf
```
systemctl start chronograf
systemctl enable chronograf
```


## Configure Chronograf
### Manipulate chronograf's systemd service
We need to manipulate chronografs systemd service. The reason for this is, that chronograf hasn't a config file. So it can be configured with system enviroment variables or with the command line parameters during startup.
> We prefer command line parameters because they are persistent
Copy the systemd file to the new location
```
cp  /usr/lib/systemd/system/chronograf.service /etc/systemd/system/chronograf.service
```
Manipulate the new systemd file as follows:
```
vi /etc/systemd/system/chronograf.service

# If you modify this, please also make sure to edit init.sh

[Unit]
Description=Open source monitoring and visualization UI for the entire TICK stack.
Documentation="https://www.influxdata.com/time-series-platform/chronograf/"
After=network-online.target

[Service]
User=chronograf
Group=chronograf
#Environment="HOST=0.0.0.0"
Environment="HOST=127.0.0.1"
Environment="PORT=8888"
Environment="BOLT_PATH=/var/lib/chronograf/chronograf-v1.db"
Environment="CANNED_PATH=/usr/share/chronograf/canned"
EnvironmentFile=-/etc/default/chronograf
ExecStart=/usr/bin/chronograf $CHRONOGRAF_OPTS
KillMode=control-group
Restart=on-failure

[Install]
WantedBy=multi-user.target

```
Reload systemd and activate the changes
```
systemctl daemon-reload
systemctl enable chronograf
systemctl start chronograf
```

### Create nginx config for chronograf
```
systemctl daemon-reload
systemctl enable chronograf
systemctl start chronograf
```


### Get letsencrypt certificate for chronograf




# Grafana
## Install Grafana
```
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-5.2.4-1.x86_64.rpm 
yum localinstall grafana-5.2.4-1.x86_64.rpm 
```

## Enable and start the service
```
systemctl enable grafana-server
systemctl start grafana-server
```

## Configure Grafana



## Configure SELinux for the droplet
We need to enable the following selinux booleans:
```
getsebool httpd_can_network_connect 
setsebool -P httpd_can_network_connect on
getsebool httpd_can_network_connect 

getsebool nis_enabled 
setsebool -P nis_enabled on
getsebool nis_enabled 
```






# Telegraf configuration on Raspbian

## Installation
```
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -

echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

sudo apt update

sudo apt install telegraf

```

## Configuration of /etc/telegraf/telegraf.conf
### Connection to InfluxDB to telegraf
```
[[outputs.influxdb]]
  urls = ["https://influxdb01.monitor.agora-space.com:8066"]
  database = "telegraf"
  skip_database_creation = false
  retention_policy = ""
  write_consistency = "any"
  timeout = "10s"
  username = "telegraf"
  password = "******"
  user_agent = "telegraf"
  content_encoding = "identity"
```
### Connection to InfluxDB to the energy-monitor
```
[[outputs.influxdb]]
  urls = ["https://influxdb01.monitor.agora-space.com:8066"]
  database = "energy-monitor"
  skip_database_creation = true
  retention_policy = ""
  write_consistency = "any"
  timeout = "15s"
  username = "energy-monitor"
  password = "ChoendSelberOebbisWehle"
  user_agent = "telegraf-energy"
  content_encoding = "identity"
  tagexclude = ["influxdb_database"]
  [outputs.influxdb.tagpass]
    influxdb_database = ["energy-monitor"]
```
### HTTP requests
```
[[inputs.http_response]]
    name_override = "google_https"
    address = "https://www.google.com/search"
    response_timeout = "10s"
    method = "GET"
    follow_redirects = true
    [[inputs.http_response.tags]]
        location = "coderbunker"
        room = "bunker-1"

[[inputs.http_response]]
    name_override = "google_docs_https"
    address = "https://docs.google.com/"
    response_timeout = "10s"
    method = "GET"
    follow_redirects = true
    [[inputs.http_response.tags]]
        location = "coderbunker"
        room = "bunker-1"

[[inputs.http_response]]
    name_override = "facebook_https"
    address = "https://facebook.com/"
    response_timeout = "10s"
    method = "GET"
    follow_redirects = true
    [[inputs.http_response.tags]]
        location = "coderbunker"
        room = "bunker-1"
```
### ping requests
```
[[inputs.ping]]
    urls = ["8.8.8.8"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "google_dns_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["gitlab.com"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "gitlab_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["github.com"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "github_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["www.pypi.org"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "pypi_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["www.slack.com"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "slack_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["10.1.0.1"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "router_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["10.1.0.2"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "gateway_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["10.1.0.64"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "hp_printer_icmp"
        location = "coderbunker"
        room = "bunker-1"

[[inputs.ping]]
    urls = ["10.1.0.104"]
    count = 5
    ping_interval = 1.0
    timeout = 10.0
    [inputs.ping.tags]
        name = "brother_printer_icmp"
        location = "coderbunker"
        room = "bunker-1"
```
### Arduino energy monitor UDP request acknowledge
```
[[inputs.socket_listener]]
      service_address = "udp://:6969"
      max_connections = 128
      read_timeout = "30s"
      read_buffer_size = 65535
      keep_alive_period = "5m"
      https://github.com/influxdata/telegraf/blob/master/docs/DATA_FORMATS_INPUT.md
      data_format = "influx"

[inputs.socket_listener.tags]
      influxdb_database = "energy-monitor"
```

## Explanation for a new Raspberry Pi
In order to rollout a new Raspberry Pi, you just need to install telegraf (like mentioned above) and use the telegraf.conf file in this repository. Afterwards you need to adjust those entries in the telegraf.conf file:

- [global_tags] (adjust the location & room)
- [agent] (adjust hostname)
- [inputs.socket_listener] + [inputs.socket_listener.tags] (comment those entries out if you install a additional Pi. These entries are only needed for the Pi "SuperNanny 2 (10.1.0.230) because the arduinos send their UDP requests directly to this pi (hardcoded on arduino))
- [inputs.*] (adjust your http/s and ICMP requests for your needs)