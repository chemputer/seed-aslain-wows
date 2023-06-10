import requests
import os
import libtorrent as lt
import time
import requests
from bs4 import BeautifulSoup
import schedule

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
            download_and_seed(torrent_link)
        else:
            print("No new torrent link found.")
    else:
        print("No torrent link found.")


def download_and_seed(torrent_link):
    # Initialize the torrent session
    ses = lt.session()
    ses.listen_on(6881, 6891)
    ses.set_download_rate_limit(1000000)  # Adjust download rate limit if needed
    ses.set_upload_rate_limit(1000000)  # Adjust upload rate limit if needed
    ses.set_alert_mask(lt.alert.category_t.error_notification
                   | lt.alert.category_t.storage_notification
                   | lt.alert.category_t.status_notification)

    # Download the new torrent file
    response = requests.get(torrent_link)
    torrent_path = os.path.basename(torrent_link)
    with open(torrent_path, 'wb') as f:
        f.write(response.content)

    # Load the torrent file and add it to the session for downloading
    info = lt.torrent_info(torrent_path)
    h = ses.add_torrent({'ti': info, 'save_path': '.'})

    # Start the downloading process
    print('Downloading:', h.name())
    while not h.is_seed():
        s = h.status()
        print('Downloading: {}% complete (down: {} kB/s up: {} kB/s peers: {})'.format(
            s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers))
        time.sleep(1)

    # Start the seeding process
    h.set_flags(lt.torrent_flags.seed_mode)
    print('Seeding:', h.name())
    while True:
        s = h.status()
        print('Seeding (up: {} kB/s peers: {})'.format(
            s.upload_rate / 1000, s.num_peers))
        time.sleep(1)


def check_webpage():
    # Schedule the scraping task to run every hour
    schedule.every(4).hours.do(scrape_webpage)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


# Start monitoring the webpage for changes
first_start = 0
if first_start == 0:
    scrape_webpage()
    first_start = 1

check_webpage()
