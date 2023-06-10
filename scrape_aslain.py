import requests
from bs4 import BeautifulSoup
import schedule
import time
import urllib.parse
from config import BASE_RSS_URL


def send_to_rss(link):
    base_url = BASE_RSS_URL 
    value = "example value"

# Encode the value
    encoded_value = urllib.parse.quote(link, safe='')

# Append the encoded value to the URL
    url = base_url + "?value1=" + encoded_value

# Send the GET request
    response = requests.get(url)

# Check the response status code
    if response.status_code == requests.codes.ok:
        # Successful request
        print("Request was successful")
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)
# File to store the previous link
previous_link_file = "previous_link.txt"
def get_previous_link():
    try:
        with open(previous_link_file, "r") as file:
            previous_link = file.read().strip()
    except FileNotFoundError:
        previous_link = ""
    
    return previous_link

def update_previous_link(new_link):
    with open(previous_link_file, "w") as file:
        file.write(new_link)

def scrape_webpage():
    url = "https://aslain.com/index.php?/topic/2020-download-%E2%98%85-world-of-warships-%E2%98%85-modpack"  # Replace with the actual URL of the webpage you want to scrape
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all the links on the webpage
    links = soup.find_all("a")
    
    # Search for the first link ending in ".torrent"
    torrent_link = None
    for link in links:
        href = link.get("href")
        if href and href.endswith(".torrent"):
            torrent_link = href
            break
    
    if torrent_link:
        previous_link = get_previous_link()
        if torrent_link != previous_link:
            print("Found a new torrent link:", torrent_link)
            update_previous_link(torrent_link)
            send_to_rss(torrent_link)
            # Perform the desired action with the torrent link, such as downloading it or saving it
        else:
            print("No new torrent link found.")
    else:
        print("No torrent link found.")

def check_webpage():
    # Schedule the scraping task to run every hour
    schedule.every(4).hours.do(scrape_webpage)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start monitoring the webpage for changes
check_webpage()
#scrape_webpage()
