#!/usr/bin/env python3
'''
    - This script was developed to communicate ssh with Cisco sandbox labs (Always-on) IOSXR.
    - To access the used lab, please use this link:
        https://devnetsandbox.cisco.com/RM/Diagram/Index/e83cfd31-ade3-4e15-91d6-3118b867a0dd?diagramType=Topology 
'''
__author__ = "Alanoud Alfawzan"
__author_email__ = "alanoud.alfawzan@gmail.com"

# import connect handler function from netmiko
from netmiko import ConnectHandler
# credential to login ssh to the router
username = 'admin'
password = 'C1sco12345'
# command list
command_list = ['show running-config', 'show inventory']
# use hostname or IP address to ligin to the network device
host_dict = {'devnet_lab': 'sandbox-iosxr-1.cisco.com'}

def login(host):
    ''' This function will start access router and return ssh connection'''
    connection = ConnectHandler(
                host = host,
                username = username,
                password = password,
                device_type = 'cisco_ios'
                )
    return connection

def main():
    ''' This function start sending command after getting the ssh connection,
        then store the output into text file.
    ''' 
    for key, host in host_dict.items():
        connection = login(host)
        command1 = connection.send_command(command_list[0])
        command2 = connection.send_command(command_list[1])
        with open(f'{key}_output.txt', 'w') as f:
            f.write('#'*30)
            f.write('  Output Of Show Running Config  ')
            f.write('#'*30)
            f.write('\n')
            f.write(command1)
            f.write('#'*30)
            f.write('  Output Of Show Inventory  ')
            f.write('#'*30)
            f.write('\n')
            f.write(command2)
   
if __name__ == "__main__":
    main()
