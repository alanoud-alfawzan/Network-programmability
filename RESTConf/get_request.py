#!/usr/bin/env python3
'''
    - This script was developed to communicate with Cisco sandbox labs (Always-on) IOSXE using RESTAPI.
    - Use get http function to retrive interfaces information using ietf yang files.
    - To access the used lab, please use this link:
        https://devnetsandbox.cisco.com/RM/Diagram/Index/27d9747a-db48-4565-8d44-df318fce37ad?diagramType=Topology 
'''
__author__ = "Alanoud Alfawzan"
__author_email__ = "alanoud.alfawzan@gmail.com"

# need to pip install requests library first
import requests
# Disable warnings messages 
requests.packages.urllib3.disable_warnings()
# devnet lab cred
username = 'developer'
password = 'C1sco12345'
# used ietf-interfaces:interfaces from ietf yang files
url = "https://sandbox-iosxe-recomm-1.cisco.com/restconf/data/ietf-interfaces:interfaces"
headers = {'Content-Type': 'application/yang-data+json','Accept': 'application/yang-data+json'}
response = requests.get(url, auth=(username, password), headers=headers, verify=False).json()
print("\nBelow are the outputs of IOS XE on CSR using Always On Sandbox provided from Cisco\n")
print("_"*85)
# loop through all the output and filter the needed keys
for data in response['ietf-interfaces:interfaces']['interface']:
    name = data['name']
    print(f"Interface Name: {name}")
    if 'description' in data.keys():
        description = data['description']
        print(f"Interface Description: {description}")
    else:
        print(f"Interface Description: N/A")
    if data['ietf-ip:ipv4']:
        ip = data['ietf-ip:ipv4']['address'][0]['ip']
        netmask = data['ietf-ip:ipv4']['address'][0]['netmask']
        print(f"IP Adress: {ip}")
        print(f"Subnet Mask: {netmask}")
    else:
        print(f"IP Adress: N/A")
        print(f"Subnet Mask: N/A")
    print("_"*50)
