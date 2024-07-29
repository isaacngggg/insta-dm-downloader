
import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import sys
import urllib.request
import ssl

# Load the CA certificate file
ca_cert_path = 'ca.crt'
context = ssl.create_default_context(cafile=ca_cert_path)

def authenticate( client: Client, session_file: str):
    if os.path.exists(session_file):
        client.load_settings(session_file)
        try:
            client.login(username, password)
            client.get_timeline_feed()  # check if the session is valid
        except LoginRequired:
            # session is invalid, re-login and save the new session
            client.login(username, password)
            client.dump_settings(session_file)
    else:
        try:
            client.login(username, password)
            client.dump_settings(session_file)
        except Exception as e:
            print(f"Failed to login: {e}")
            sys.exit(1)

username = os.environ.get("IG_USERNAME")
email = os.environ.get("IG_EMAIL")
password = os.environ.get("IG_PASSWORD")

cl = Client()
# Test without proxy
before_ip = cl._send_public_request("https://api.ipify.org/")
print(f"Before: {before_ip}")

# Set proxy and test again
cl.set_proxy('brd-customer-hl_9227f0cb-zone-mobile_proxy1:wx37igen0yfi@brd.superproxy.io:22225')
after_ip = cl._send_public_request("https://api.ipify.org/")
print(f"After: {after_ip}")

authenticate(cl, "session.json")

