#!/usr/bin/env python3

'''
    - This script was developed to communicate with ACI APIC controller using REST API.
    - Cisco devnet lab was used un this code.
    - To access the used lab, please use this link:
        https://devnetsandbox.cisco.com/RM/Diagram/Index/18a514e8-21d4-4c29-96b2-e3c16b1ee62e?diagramType=Topology
'''

__author__ = "Alanoud Alfawzan"
__author_email__ = "alanoud.alfawzan@gmail.com"


# import request library to use API
import requests
from pprint import pprint
# credential to login APIC GUI
username = 'admin'
password = '!v3G@!4@Y'

# Disable warnings messages
requests.packages.urllib3.disable_warnings() 

def get_token(username, password):
    " This function will generate and return token with APIC"
    # APIC ip address in url to get the token
    apic_url = f"https://sandboxapicdc.cisco.com/api/aaaLogin.json"
    # Payload contains authentication information
    payload = { "aaaUser": {"attributes": {"name": username,"pwd": password}}}
    # Header information
    headers = {"content-type": "application/json"}
    response = requests.post(apic_url, json = payload, headers = headers, verify = False).json()
    # Return authentication token from respond body
    token = response['imdata'][0]['aaaLogin']['attributes']['token']
    return token  
    
def get_device_info(token): 
    "this function will return devices Name, Role, and IP-Address"
    # url to get all hostnames and device model in APIC
    url = f"https://sandboxapicdc.cisco.com/api/node/class/fabricNode.json?"
    # Header information"
    headers = {'Cookie': 'APIC-cookie='+token}
    response = requests.get(url, headers=headers, verify=False).json()
    pprint('Total number of devices in the fabric: {}'.format(response['totalCount']))
    for endpoints in response['imdata']:
        for endpoint_data in endpoints["fabricNode"].items():
            pprint('Device Name: {}'.format(endpoint_data[1]['name']))
            pprint('Device Role: {}'.format(endpoint_data[1]['role']))
            pprint('Device Address: {}'.format(endpoint_data[1]['address']))
            pprint("#" * 30)
            
def main():            
    token = get_token(username, password)
    get_device_info(token)


if __name__ == "__main__":
    main()
