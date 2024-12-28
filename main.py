import base64
import random
import time
import uuid
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
from flask import Flask, render_template, request

# Load environment variables
load_dotenv()

# Set up ProxyMesh (Credentials and regions from .env file)
PROXYMESH_USER = os.getenv('PROXYMESH_USER')
PROXYMESH_PASSWORD = os.getenv('PROXYMESH_PASSWORD')
proxy_regions = os.getenv('PROXY_REGIONS', 'us,ca,uk,eu,in,au').split(',')

# Set up MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['twitter_trends']
collection = db['trends']

# Set up Flask app
app = Flask(__name__)

# Function to fetch Twitter trends with ProxyMesh
def fetch_twitter_trends():
    # Select a random proxy region from the list
    region = random.choice(proxy_regions)
    proxy_url = f'http://{PROXYMESH_USER}:{PROXYMESH_PASSWORD}@{region}-ca.proxymesh.com:31280'
    encoded_credentials = base64.b64encode(f'{PROXYMESH_USER}:{PROXYMESH_PASSWORD}'.encode()).decode()
    proxy_url = f'http://{encoded_credentials}@{region}-ca.proxymesh.com:31280'
    print(f"Using ProxyMesh proxy: {proxy_url}")

    # Set up the proxy configuration for Selenium
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy_url}')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://x.com/i/flow/login")

        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')

        # Log in to Twitter
        time.sleep(7)
        driver.find_element(By.XPATH, "//input").send_keys(username + Keys.RETURN)

        time.sleep(7)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password + Keys.RETURN)
        time.sleep(10)

        # Get IP address
        response = requests.get('https://api.ipify.org')
        ip_address = response.text
        print(f"Current IP Address: {ip_address}")

        # Get Trending Topics
        trending_topics = driver.find_elements(By.XPATH, "//div[@aria-label='Timeline: Trending now']//span")
        top_trends = [trend.text for trend in trending_topics]
        print("Trending topics found: ", top_trends)

        # Filter out empty or irrelevant topics
        what_happening = []
        i = 0
        while i < len(top_trends) - 1:
            if "Trending" in top_trends[i]:
                i += 1
                what_happening.append(top_trends[i])
            i += 1

        print("Trending Topics: ", what_happening)

        # Ensure we have exactly 5 topics, append placeholders if needed
        while len(what_happening) < 5:
            what_happening.append("No additional trending topics found")

        # Prepare data for MongoDB
        unique_id = str(uuid.uuid4())
        data = {
            "_id": unique_id,
            "nameoftrend1": what_happening[0],
            "nameoftrend2": what_happening[1],
            "nameoftrend3": what_happening[2],
            "nameoftrend4": what_happening[3],
            "nameoftrend5": what_happening[4],
            "datetime": datetime.now(),
            "ip_address": ip_address
        }

        # Insert data into MongoDB
        try:
            collection.insert_one(data)
            print("Data successfully inserted into MongoDB")
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")

        # Return the data for display
        return data

    except Exception as e:
        print(f"Error in fetching trends: {e}")

    finally:
        # Ensure the driver is always quit properly
        driver.quit()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['POST'])
def run_script():
    data = fetch_twitter_trends()
    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
