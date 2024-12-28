import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up ProxyMesh (Credentials from .env file)
PROXYMESH_USER = os.getenv('PROXYMESH_USER')
PROXYMESH_PASSWORD = os.getenv('PROXYMESH_PASSWORD')

# Define the specific region
region = 'us-ca'
proxy_url = f'http://{PROXYMESH_USER}:{PROXYMESH_PASSWORD}@{region}.proxymesh.com:31280'

print(f"Using ProxyMesh proxy: {proxy_url}")

# Test the proxy
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
