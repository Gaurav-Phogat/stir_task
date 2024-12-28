import requests
from dotenv import load_dotenv
import os

load_dotenv()

PROXYMESH_USER = os.getenv('PROXYMESH_USER')
PROXYMESH_PASSWORD = os.getenv('PROXYMESH_PASSWORD')

region = 'us-ca'
proxy_url = f'http://{PROXYMESH_USER}:{PROXYMESH_PASSWORD}@{region}.proxymesh.com:31280'

print(f"Using ProxyMesh proxy: {proxy_url}")

proxy = {
    "http": proxy_url,
    "https": proxy_url,
}

try:
    response = requests.get('https://api.ipify.org', proxies=proxy)
    ip_address = response.text
    print(f"Current IP Address: {ip_address}")
except Exception as e:
    print(f"Error testing proxy: {e}")
