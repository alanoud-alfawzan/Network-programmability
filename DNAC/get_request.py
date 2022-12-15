#!/usr/bin/env python3
'''
    - This script was developed to communicate with Cisco sandbox DNAC labs (Always-on) using RESTAPI.
    - Use http get function to retrive information from DNAC.
    - To access the used lab, please use this link:
        https://devnetsandbox.cisco.com/RM/Diagram/Index/471eb739-323e-4805-b2a6-d0ec813dc8fc?diagramType=Topology
'''
__author__ = "Alanoud Alfawzan"
__author_email__ = "alanoud.alfawzan@gmail.com"



import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()
information = {
                "host": "sandboxdnac2.cisco.com",
                "username": "dnacdev",
                "password": "D3v93T@wK!"
              }

def get_auth_token():
    """ 
    This function will return the token from DNAC controller. 
    """
    url = "https://{}/dna/system/api/v1/auth/token".format(information['host'])
    # to get the token we need to use post request
    response = requests.post(url, auth=HTTPBasicAuth(information['username'], information['password']), verify=False)
    # convert the output to json and get the token key value
    token = response.json()['Token']
    # return the token to be used with other DNAC requests
    return token

def get_device_list(token):
    """
    Building out function to retrieve all information and present it in nice formatt. 
    """
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    url = "https://{}/api/v1/network-device".format(information['host'])
    header = {'x-auth-token': token, 'content-type' : 'application/json'}
    response = requests.get(url, headers=header, verify=False).json()  
    print(f"How many device in the fabric: {len(response['response'])}")
    for device in response['response']:
        list1.append(device['role'])
        list2.append(device['softwareType'])
        list3.append(device['platformId'])
        list4.append(device['managementIpAddress'])
    #create dataframe from the college data
    data= pd.DataFrame({
                        "Device Role":list1,
                        "Software Type":list2,
                        "Platform Type":list3,
                        "Mangment IP":list4},
                        index=[1, 2, 3])
    #display the dataframe
    print(data)
    
if __name__ == "__main__":
    token = get_auth_token()
    get_device_list(token)
   