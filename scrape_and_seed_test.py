import requests
import os
import libtorrent as lt
import time
import requests
from bs4 import BeautifulSoup
import schedule

# File to store the previous link
previous_link_file = "previous_link.txt"
save_dir = os.path.join(os.getcwd(), 'Torrent_Downloads')  # Replace 'downloads' with your desired directory name

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
    url = "https://aslain.com/index.php?/topic/2020-download-%E2%98%85-world-of-warships-%E2%98%85-modpack"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    torrent_link = next((link.get("href") for link in soup.find_all("a") if link.get("href") and link.get("href").endswith(".torrent")), None)

    if torrent_link:
        previous_link = get_previous_link()
        if torrent_link != previous_link:
            print("Found a new torrent link:", torrent_link)
            update_previous_link(torrent_link)
            download_and_seed(torrent_link)
        else:
            print("No new torrent link found. Resuming seeding...")
            resume_seeding()
    else:
        print("No torrent link found.")


def download_and_seed(torrent_link):
    # Initialize the torrent session
    ses = lt.session()
    ses.listen_on(6881, 6891)
    # ses.set_download_rate_limit(1000000)  # Adjust download rate limit if needed
    # ses.set_upload_rate_limit(1000000)  # Adjust upload rate limit if needed

    # Download the new torrent file
    response = requests.get(torrent_link)
    torrent_path = os.path.join(save_dir, os.path.basename(torrent_link))
    with open(torrent_path, 'wb') as f:
        f.write(response.content)

    # Load the torrent file and add it to the session for seeding
    info = lt.torrent_info(torrent_path)
    h = ses.add_torrent({'ti': info, 'save_path': save_dir})

    # Start the seeding process
    h.set_flags(lt.torrent_flags.seed_mode)
    print('Seeding:', h.name())
    while True:
        s = h.status()
        print('Seeding (up: {} kB/s peers: {})'.format(
            s.upload_rate / 1000, s.num_peers))
        time.sleep(1)


def resume_seeding(): 
    # Initialize the torrent session
    ses = lt.session()
    ses.listen_on(6881, 6891)
    #ses.set_download_rate_limit(1000000)  # Adjust download rate limit if needed
    #ses.set_upload_rate_limit(1000000)  # Adjust upload rate limit if needed

    # Find the resume file in the save directory
    resume_files = [f for f in os.listdir(save_dir) if f.endswith(".resume")]
    if not resume_files: 
        print("No resume file found. Unable to resume seeding.")
        return
    torrent_files = [f for f in os.listdir(save_dir) if f.endswith(".torrent")]
    torrent_path = os.path.join(save_dir,torrent_files[0])
    # Load the original torrent file
    with open(torrent_path, "rb") as file: 
        torrent_data = file.read()

       # Create a torrent handle using the original torrent data
    h = ses.add_torrent({'ti': lt.torrent_info(torrent_data), 'save_path': save_dir})

    # Start the seeding process
    h.set_flags(lt.torrent_flags.seed_mode)
    print('Resuming seeding:', h.name())
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
if __name__ == "__main__":
    scrape_webpage()
    check_webpage()
