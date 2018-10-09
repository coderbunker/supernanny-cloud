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
enabled = 
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
vi /etc/firewalld/services/coderbunker-influxdb.xml
```
```
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>CoderBunker-InfluxDB</short>
  <description>CoderBunker InfluxDB for the Super Nanny Project</description>
  <port protocol="tcp" port="8086 "/>
</service>
```
### Reload the firewall and enable the service permanent
```
firewall-cmd --reload
firewall-cmd --add-service=coderbunker-influxdb --zone=public --permanent
firewall-cmd --reload
```

## Configure InfluxDB
### Adding users
We need the following users:
 - chronograf - admin

PW's are stored in teh spreedshirt.

Creating admin user:
```
CREATE USER <USER> WITH PASSWORD '<PASSWORD>' WITH ALL PRIVILEGES
```

Creating non-admin user:
```
CREATE USER <USER> WITH PASSWORD '<PASSWORD>'
```
More at: https://docs.influxdata.com/influxdb/v1.6/administration/authentication_and_authorization/






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
### Create firewalld service
```
vi /etc/firewalld/services/coderbunker-chronograf.xml
```
```
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>CoderBunker-Chronograf</short>
  <description>CoderBunker Chronograf for the Super Nanny Project</description>
  <port protocol="tcp" port="8888 "/>
</service>
```
### Reload the firewall and enable the service permanent
```
firewall-cmd --reload
firewall-cmd --add-service=coderbunker-chronograf --zone=public --permanent
firewall-cmd --reload
```

## Configure Chronograf
### Manipulate chronograf's systemd service
We need to manipulate chronografs systemd service. The reason for this is, that chronograf hasn't a config file. So it can be configured with system enviroment variables or with the command line parameters during startup.
> We prefere comannd line parameters because they are presistent
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

# Telegraf configuration on Raspbian

```
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt update
sudo apt install influxdb telegraf
```




