#!/usr/bin/python3

import json
import os

__DEBUG_ONLY__ = False
__ROOT__ = '/'

class System:
    def __init__(self):
        self.packages = '' 
        self.settings = ''

    def install(self, packages):
        # combine list of packages into a string
        # make system call to install them
        self.packages = packages
        inst_string =""
        for ind, val in enumerate(self.packages):
            inst_string += " " + val
        inst_string += " "
        if __DEBUG_ONLY__:
            print("DEBUG: Installing packages: "+inst_string)
            return
        # adding keys for docker repo 
        os.system('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg')
        # adding docekr repo
        os.system('echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null')
        os.system('apt update')
        # install additional packages
        os.system('apt -y install' + inst_string )
        # download compose binary
        os.system('curl -L "https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
        os.system('chmod +x /usr/local/bin/docker-compose')

    def parse(self, settings):
        # parse all settings and depending on what each one is calling associated variable
        self.settings = settings
        for ind, val in enumerate(self.settings):
            for key, value in val.items():
                if "ufw" == key:
                    self.configure_ufw(value)
    
    def configure_ufw(self, ufw_settings):
        # get UFW settings from config file 
        # apply UFW configuration
        if __DEBUG_ONLY__:
            print("DEBUG COnfiguring UFW")
            return

    def configure_resolved(self):
        # disable resolved listener
        if __DEBUG_ONLY__:
            print("DEBUG Configured resolved listener")
            return
        os.system('mkdir -p /etc/systemd/resolved.conf.d/')
        os.system('echo "[Resolve]\nDNSStubListener=no" > /etc/systemd/resolved.conf.d/disable-stub.conf')
        os.system('ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf')
        os.system('systemctl restart systemd-resolved')


class Service:
    def __init__(self,service_description):
        self.service_data = service_description
        self.default_folder = os.path.join(__ROOT__,"ethiork")

    def deploy(self):
        # create root folder
        self.create_defaults()
        # this is deployment for each service
        for ind, val in enumerate(self.service_data):
            for key, value in val.items():
                # copy templates
                self.copy_templates(service_name=key)
                # update variables
                self.update_templates(service_name=key, service_vars=value)
                # launch setvice
                self.launch(service_name = key)
    
    def create_defaults(self):
        # creare root folder
        if __DEBUG_ONLY__:
            print("DEBUG Create default folder")
            return
        os.system('mkdir -p ' + self.default_folder)
        os.system('systemctl restart docker.socket docker.service')

    def copy_templates(self, service_name):
        # copy templates folders
        if __DEBUG_ONLY__:
            print("DEBUG Copy remplates")
            return
        os.system('mv services/'+service_name+' ' + self.default_folder + '/')

    def update_templates(self, service_name, service_vars):
        # update docker variables
        if "dns" == service_name:
            # updating pihole
            # open docker file
            file_name = os.path.join(self.default_folder, service_name, 'docker-compose.yml') 
            with open(file_name, 'r') as docker_file:
                docker_config = docker_file.read()
                for key, value in service_vars.items():
                    # find and replase
                    docker_config = docker_config.replace(key,value)
            if __DEBUG_ONLY__:
                print("DEBUG Writing config")
                return
            with open(file_name, 'w') as docker_file:
                docker_file.write(docker_config)
        elif "ddns" == service_name:
            # update ddns
            if __DEBUG_ONLY__:
                print("DEBUG Update ddns service")
                return
        elif "wireguard" == service_name:
            # update wireguard
            if __DEBUG_ONLY__:
                print("DEBUG Update wireguard service")
                return

    def launch(self, service_name):
        #launching service
        if __DEBUG_ONLY__:
            print("DEBUG Launching service:" + service_name)
            return
        folder_name = os.path.join(self.default_folder,service_name)
        os.system('cd ' + folder_name + '; docker-compose up -d')



class Config:
    def __init__(self,config_file):
        self.config_file = config_file
        self.config_data = {}
    
    def load(self):
        # Read JSON file
        with open(self.config_file,"r") as config:
            self.config_data = json.load(config)
    
    def save(self):
        if __DEBUG_ONLY__:
            print("DEBUG Writing JSON file")
            return
        with open(self.config_file, "w") as config:
            json.dump(self.config_data, config, indent=4)

    def generate(self):
        # this one will generate missing parameters if necesary
        # executing recursive loop through JSON
        self.config_data = self.recursive_iteration(self.config_data)

    def _gen_data(self,data_key, data_value):
        # set of ifs that woudl generate nessecary data for us
        if "_insert_ip_" == data_value:
            # getting up from machine
            with os.popen("ip route get 1 | awk '{print $(NF-2);exit}'") as system_pipe:
                data_value = system_pipe.read().rstrip()
        elif "_insert_pass_" == data_value:
            # generating randome password
            with os.popen('< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;') as system_pipe:
                data_value = system_pipe.read().rstrip()
        return data_value

    def recursive_iteration(self, json_data, current_level=0):
        if isinstance(json_data, dict):
            # we've got simple dictionary
            for key, value in json_data.items():
                if isinstance(value, (dict,list)):
                    # recursive call
                    self.recursive_iteration(json_data = value, current_level = current_level + 1)
                else:
                    # we are at the end generate data
                    json_data[key] = self._gen_data(data_key = key, data_value = value)
        elif isinstance(json_data, list):
            # we've got an array
            for ind, item in enumerate(json_data):
                if isinstance(item, (dict, list)):
                    # recursive call
                    self.recursive_iteration(json_data = item, current_level = current_level +1)
                else:
                    # we are at the end generate data
                    json_data[ind] = self._gen_data(data_key = ind, data_value = item)
        return json_data

    def process(self):
        # this method will process and deploy services
        for key, value in self.config_data.items():
            if "packages" == key:
                # installing packages
                packages = value
            if "settings" == key:
                # applying settings
                settings = value
            if "services" == key:
                services_list = value
        server = System()
        # first we install packages
        server.install(packages)
        # configure system things
        server.parse(settings)
        server.configure_resolved()
        # loop through set of services
        # and deploy each one
        services = Service(services_list)
        services.deploy()

# Prepare Ubuntu installation to make sure all dependencies are met
# Configure UFW to lock everything except wireguard port for incoming connections
# Configure outgoing connections limiting to only that we know are required
 

# read ethiork.json
# parse services that needs to be deploy
# deploy each of the services

if __name__ == "__main__":
    ethiork = Config(config_file="ethiork.json")
    ethiork.load()
    ethiork.generate()
    ethiork.save()
    ethiork.process()