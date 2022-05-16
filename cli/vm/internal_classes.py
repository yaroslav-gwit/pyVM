# native imports
import json
import os
import subprocess
import random
import sys

# 3rd party imports
from jinja2 import Template
from generate_mac import generate_mac
import yaml

# internal imports
# from cli.dataset import internal_classes as DatasetIC

# STANDALONE FUNCTIONS
def random_password_generator(capitals:bool = False, numbers:bool = False, lenght:int = 8, specials:bool = False):
    letters_var = "asdfghjklqwertyuiopzxcvbnm"
    capitals_var = "ASDFGHJKLZXCVBNMQWERTYUIOP"
    numbers_var = "0987654321"
    specials_var = ".,-_!^*?><)(%[]=+$#"
    
    valid_chars_list = []
    for item in letters_var:
        valid_chars_list.append(item)
    if capitals:
        for c_item in capitals_var:
            valid_chars_list.append(c_item)
    if numbers:
        for n_item in numbers_var:
            valid_chars_list.append(n_item)
    if specials:
        for s_item in specials_var:
            valid_chars_list.append(s_item)
    
    password = ""
    for _i in range(0, lenght):
        password = password + random.choice(valid_chars_list)
    
    return password

def mac_address_generator(prefix:str = "58:9C:FC"):
    mac_addess = generate_mac.vid_provided(prefix)
    mac_addess = mac_addess.lower()
    return mac_addess


# CLASSES
class CloudInit:
    def __init__(self, vm_name, vm_folder, vm_ssh_keys, os_type, ip_address, network_bridge_address,
                    root_password, user_password, mac_address, new_vm_name=False, old_zfs_ds=False, new_zfs_ds=False):
        
        self.vm_name = vm_name
        self.vm_folder = vm_folder
        self.new_vm_name = new_vm_name

        self.old_zfs_ds = old_zfs_ds
        self.new_zfs_ds = new_zfs_ds

        self.output_dict = {}
        self.output_dict["random_instanse_id"] = random_password_generator(lenght=5)
        self.output_dict["vm_name"] = vm_name
        self.output_dict["mac_address"] = mac_address
        self.output_dict["os_type"] = os_type
        self.output_dict["ip_address"] = ip_address
        self.output_dict["network_bridge_address"] = network_bridge_address
        self.output_dict["vm_ssh_keys"] = vm_ssh_keys
        self.output_dict["root_password"] = root_password
        self.output_dict["user_password"] = user_password


    def rename(self):
        # Check if VM exists
        # vm_name = self.vm_name
        new_vm_name = self.new_vm_name

        old_zfs_ds = self.old_zfs_ds
        new_zfs_ds = self.new_zfs_ds

        new_vm_folder = self.vm_folder
        output_dict = self.output_dict
        output_dict["vm_name"] = new_vm_name

        cloud_init_files_folder = new_vm_folder + "/cloud-init-files"
        if not os.path.exists(cloud_init_files_folder):
            sys.exit(" ⛔ CRITICAL: CloudInit folder doesn't exist here: /" + old_zfs_ds)

        # Read Cloud Init Metadata
        with open("./templates/cloudinit/meta-data", "r") as file:
            md_template = file.read()
        # Render Cloud Init Metadata Template
        md_template = Template(md_template)
        md_template = md_template.render(output_dict=output_dict)
        # Write Cloud Init Metadata Template
        with open(cloud_init_files_folder + "/meta-data", "w") as file:
            file.write(md_template)

        # Create ISO file
        command = "genisoimage -output " + new_vm_folder + "/seed.iso -volid cidata -joliet -rock " + cloud_init_files_folder + "/user-data " + cloud_init_files_folder + "/meta-data " + cloud_init_files_folder + "/network-config"
        # print(command)
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        # Rename ZFS dataset
        # Check if VM is Live
        command = "zfs rename " + old_zfs_ds + " " + new_zfs_ds
        # print(command)
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)


    def reset(self):
        vm_name = self.vm_name
        output_dict = self.output_dict
        vm_folder = self.vm_folder

        cloud_init_files_folder = vm_folder + "/cloud-init-files"
        if not os.path.exists(cloud_init_files_folder):
            sys.exit(" ⛔ CRITICAL: CloudInit folder doesn't exist here: " + vm_folder)

        with open("./templates/vm_config_template.json", "r") as file:
            template = file.read()

        # Render VM template
        template = Template(template)
        template = template.render(output_dict=output_dict)
        # Write VM template
        with open(vm_folder + "vm_config.json", "w") as file:
            file.write(template)

        # Read Cloud Init Metadata
        with open("./templates/cloudinit/meta-data", "r") as file:
            md_template = file.read()
        # Render Cloud Init Metadata Template
        md_template = Template(md_template)
        md_template = md_template.render(output_dict=output_dict)
        # Write Cloud Init Metadata Template
        with open(cloud_init_files_folder + "/meta-data", "w") as file:
            file.write(md_template)

        # Read Cloud Init Network Template
        with open("./templates/cloudinit/network-config", "r") as file:
            nw_template = file.read()
        # Render Cloud Init Network Template
        nw_template = Template(nw_template)
        nw_template = nw_template.render(output_dict=output_dict)
        # Write Cloud Init Network
        with open(cloud_init_files_folder + "/network-config", "w") as file:
            file.write(nw_template)

        # Read Cloud Init User Template
        with open("./templates/cloudinit/user-data", "r") as file:
            usr_template = file.read()
        # Render loud Init User Template
        usr_template = Template(usr_template)
        usr_template = usr_template.render(output_dict=output_dict)
        # Write Cloud Init User Template
        with open(cloud_init_files_folder + "/user-data", "w") as file:
            file.write(usr_template)

        # Create ISO file
        command = "genisoimage -output " + vm_folder + "/seed.iso -volid cidata -joliet -rock " + cloud_init_files_folder + "/user-data " + cloud_init_files_folder + "/meta-data " + cloud_init_files_folder + "/network-config"
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)


    def deploy(self):
        new_vm_folder = self.vm_folder
        output_dict = self.output_dict

        cloud_init_files_folder = new_vm_folder + "/cloud-init-files"
        if not os.path.exists(cloud_init_files_folder):
            os.mkdir(cloud_init_files_folder)

        # Read Cloud Init Metadata
        with open("./templates/cloudinit/meta-data", "r") as file:
            md_template = file.read()
        # Render Cloud Init Metadata Template
        md_template = Template(md_template)
        md_template = md_template.render(output_dict=output_dict)
        # Write Cloud Init Metadata Template
        with open(cloud_init_files_folder + "/meta-data", "w") as file:
            file.write(md_template)

        # Read Cloud Init Network Template
        with open("./templates/cloudinit/network-config", "r") as file:
            nw_template = file.read()
        # Render Cloud Init Network Template
        nw_template = Template(nw_template)
        nw_template = nw_template.render(output_dict=output_dict)
        # Write Cloud Init Network
        with open(cloud_init_files_folder + "/network-config", "w") as file:
            file.write(nw_template)

        # Read Cloud Init User Template
        with open("./templates/cloudinit/user-data", "r") as file:
            usr_template = file.read()
        # Render loud Init User Template
        usr_template = Template(usr_template)
        usr_template = usr_template.render(output_dict=output_dict)
        # Write Cloud Init User Template
        with open(cloud_init_files_folder + "/user-data", "w") as file:
            file.write(usr_template)

        # Create ISO file
        command = "genisoimage -output " + new_vm_folder + "/seed.iso -volid cidata -joliet -rock " + cloud_init_files_folder + "/user-data " + cloud_init_files_folder + "/meta-data " + cloud_init_files_folder + "/network-config"
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)



class ZFSReplication:
    def __init__(self):
        pass

    def pull(self):
        pass

    def push(self):
        pass