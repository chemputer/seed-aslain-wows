import feedparser
import requests
import os
import libtorrent as lt
import time

# Define the RSS feed URL
rss_feed_url = 'http://example.com/rss_feed.xml'

# Define the directory where torrent files will be saved
torrent_dir = '~/repos/rss_seeder/torrents/'

# Define the directory where downloaded files will be saved
download_dir = '~/repos/rss_seeder/downloads/'

# Define the path to the torrent client configuration file
session_file = '~/repos/rss_seeder/session.conf'

# Load the previous publication date from the session file
previous_date = None
if os.path.exists(session_file):
    with open(session_file, 'r') as f:
        previous_date = f.read().strip()

# Initialize the torrent session
ses = lt.session()
ses.listen_on(6881, 6891)
ses.set_download_rate_limit(1000000)  # Adjust download rate limit if needed
ses.set_upload_rate_limit(1000000)  # Adjust upload rate limit if needed
ses.set_alert_mask(lt.alert.category_t.error_notification
                   | lt.alert.category_t.storage_notification
                   | lt.alert.category_t.status_notification)

while True:
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)

    # Iterate over the entries in reverse order (most recent first)
    for entry in reversed(feed.entries):
        title = entry.title
        publication_date = entry.published

        # Compare the publication date with the previous date
        if publication_date > previous_date:
            # Stop seeding and delete old files
            if previous_date is not None:
                # Stop seeding the previous file
                # Delete the previous file from the disk
                pass

            # Download the new torrent file
            torrent_url = entry.link
            response = requests.get(torrent_url)
            torrent_path = os.path.join(torrent_dir, f'{title}.torrent')
            with open(torrent_path, 'wb') as f:
                f.write(response.content)

            # Load the torrent file and add it to the session for downloading
            info = lt.torrent_info(torrent_path)
            h = ses.add_torrent({'ti': info, 'save_path': download_dir})

            # Start the downloading process
            print('Downloading:', h.name())
            while not h.is_seed():
                s = h.status()
                print('Downloading: {}% complete (down: {} kB/s up: {} kB/s peers: {})'.format(
                    s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers))
                time.sleep(1)

            # Start the seeding process
            h.seed_mode(True)
            print('Seeding:', h.name())
            while True:
                s = h.status()
                print('Seeding (up: {} kB/s peers: {})'.format(
                    s.upload_rate / 1000, s.num_peers))
                time.sleep(1)

            # Save the new publication date to the session file
            with open(session_file, 'w') as f:
                f.write(publication_date)

            break  # Exit the loop after processing the most recent entry

    time.sleep(600)  # Wait for 10 minutes before checking the RSS feed again
