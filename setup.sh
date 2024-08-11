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
curl -L "https://github.com/docker/compose/releases/download/2.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# copy configuration files
# launch services
