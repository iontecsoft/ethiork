#!/bin/bash
# script suppose to be run under root, so we can ignore all requirements for passwords and all extra prompts
# installing additional system dependencies
apt install wget curl smartmontools parted ntfs-3g net-tools udevil samba cifs-utils mergerfs unzip
apt install apt-transport-https ca-certificates curl gnupg lsb-release

# adding docker repo keys
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# adding docker repo 
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
# install docker 
apt install docker-ce docker-ce-cli containerd.io
# install docker-compose
curl -L "https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# copy configuration files from temp folder where we are running that script into /ethiork folder
mkdir /ethiork
mkdir /ethiork/dns
cp -R services/dns/* /ethiork/dns/

# for pihole configuration
# get ip address of this machine and put it as server IP
# simplest way of getting IP
#SERVER_IP=`hostname -I | cut -d' ' -f1`
# this way suppose to work better
SERVER_IP=`ip route get 1 | awk '{print $(NF-2);exit}'`
sed -i -e "s/_insert_ip_/$SERVER_IP/g" /ethiork/dns/docker-compose.yml
# generate random password and ingest it as a password
PASSWD=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;`
sed -i -e "s/_insert_pass_/$PASSWD/g" /ethiork/dns/docker-compose.yml
# create service that would launch on start
# launch services
cd /ethiork/dns
docker-compose up -d