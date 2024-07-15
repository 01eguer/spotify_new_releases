import requests
import json
import os
import argparse
from datetime import datetime, timedelta, date
import subprocess

# Function to get the client token
def get_client_token():
    url = 'https://clienttoken.spotify.com/v1/clienttoken'
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://clienttoken.spotify.com/v1/clienttoken',
        'content-type': 'application/json'
    }
    data = {
        'client_data': {
            'client_version': '1.2.42.28.g8144aa96',
            'client_id': 'd8a5ed958d274c2e8ee717e6a4b0971d',
            'js_sdk_data': {
                'device_brand': 'unknown',
                'device_model': 'unknown',
                'os': 'linux',
                'os_version': 'unknown',
                'device_id': '21615417ab53b05b0bea25c63073e0a1',
                'device_type': 'computer'
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    client_token = response.json()['granted_token']['token']
    #print(f'client token: {client_token}')
    return client_token

# Function to get the access token
def get_access_token():
    url = 'https://open.spotify.com'
    response = requests.get(url)
    access_token = response.text.split('<script id="session"')[1].split('>')[1].split('<')[0]
    access_token = json.loads(access_token)['accessToken']
    #print(f'access token: {access_token}')
    return access_token


# Function to check if a id is prevously downloaded
def check_downloaded_id(file_path, ID):
    with open(file_path, 'r') as file:
        for line in file:
            if not line.startswith('#'):
                if ID in line:
                    return True
    return False

def register_downloaded_id(file_path, ID):
    with open(file_path, 'a') as file:
        file.write(f'\n{ID}')

# Function to get playlist tracks
def get_playlist_tracks(client_token, access_token, playlist_id):
    url = f'https://api-partner.spotify.com/pathfinder/v1/query?operationName=fetchPlaylistContents&variables=%7B%22uri%22%3A%22spotify%3Aplaylist%3A{playlist_id}%22%2C%22offset%22%3A0%2C%22limit%22%3A100%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2276849d094f1ac9870ac9dbd5731bde5dc228264574b5f5d8cbc8f5a8f2f26116%22%7D%7D'
    headers = {
        'Accept': 'application/json',
        'client-token': client_token,
        'authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    #print(f'response.json: {response.json}')
    return response.json()

# Function to get track release date
def get_track_release_date(client_token, access_token, track_id):
    url = f'https://api-partner.spotify.com/pathfinder/v1/query?operationName=getTrack&variables=%7B%22uri%22%3A%22spotify%3Atrack%3A{track_id}%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22ae85b52abb74d20a4c331d4143d4772c95f34757bfa8c625474b912b9055b5c0%22%7D%7D'
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json;charset=UTF-8',
        'client-token': client_token,
        'authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    #print(f'response.json: {response.json}')
    return response.json()

# Function to get artist releases
def get_artist_releases(client_token, access_token, artist_id):
    url = f'https://api-partner.spotify.com/pathfinder/v1/query?operationName=queryArtistDiscographyAll&variables=%7B%22uri%22%3A%22spotify%3Aartist%3A{artist_id}%22%2C%22offset%22%3A0%2C%22limit%22%3A18%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%229380995a9d4663cbcb5113fef3c6aabf70ae6d407ba61793fd01e2a1dd6929b0%22%7D%7D'
    headers = {
        'client-token': client_token,
        'authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to get releases newer than a given date
def get_new_releases(artist_id, comparison_date, replace):
    client_token = get_client_token()
    access_token = get_access_token()
    releases_data = get_artist_releases(client_token, access_token, artist_id)

    new_releases = []
    items = releases_data['data']['artistUnion']['discography']['all']['items']
    #print(items)
    for item in items:
        for release in item['releases']['items']:
            release_date = release['date']['isoString']
            content_id = release['id']

            if (replace or not check_downloaded_id(downloaded_file, content_id)): # this also checks if the content was previously downloaded
                register_downloaded_id(downloaded_file, content_id)

                if release_date > comparison_date:
                    new_releases.append(release['sharingInfo']['shareUrl'])

    return new_releases




# Main function to get new tracks from playlists and releases from artists
def get_new_tracks_and_releases(download_file, downloaded_file, comparison_date, replace):
    client_token = get_client_token()
    access_token = get_access_token()

    with open(download_file, 'r') as file:
        urls = file.readlines()



    new_links = []

    for url in urls:
        print(f'processing url {url}')
        url = url.strip()
        if 'playlist' in url:
            print('playlist detected')
            playlist_id = url.split('/')[-1]
            playlist_data = get_playlist_tracks(client_token, access_token, playlist_id)
            items = playlist_data['data']['playlistV2']['content']['items']

            for item in items:
                track_uri = item['itemV2']['data']['uri']
                track_id = track_uri.split(':')[2]

                # track_data = get_track_release_date(client_token, access_token, track_id)
                # release_date = track_data['data']['trackUnion']['albumOfTrack']['date']['isoString']

                if (replace or not check_downloaded_id(downloaded_file, track_id)): # this also checks if the content was previously downloaded
                    new_links.append(f'https://open.spotify.com/track/{track_id}')
                    register_downloaded_id(downloaded_file, track_id)
                    #print(f'track id {track_id}')

                # if release_date > comparison_date:
                #     new_links.append(f'https://open.spotify.com/track/{track_id}')

        elif 'artist' in url:
            #print('artist detected')
            artist_id = url.split('/')[-1]
            new_releases = get_new_releases(artist_id, comparison_date, replace)
            new_links.extend(new_releases)

    return new_links



if __name__ == "__main__":
    download_file = 'artists.txt'
    downloaded_file = '.dw'



    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--younger-than', type=int, help='Days threshold for newer items')
    parser.add_argument('--after', type=str, help='Date in D/M/Y format to compare after')
    parser.add_argument('--replace', action='store_true', help='Download even if the content was previously downloaded')
    args = parser.parse_args()



    if args.younger_than and args.after:
        print("Error: Cannot use --younger_than and --after options together.")
        exit(1)
    elif args.younger_than:
        younger_than_days = args.younger_than
        comparison_date = (datetime.now() - timedelta(days=younger_than_days)).isoformat()
    elif args.after:
        after_date_str = args.after
        try:
            day, month, year = map(int, after_date_str.split('/'))
            comparison_date = date(year, month, day).isoformat()
        except ValueError:
            print("Invalid date format. Please use D/M/Y format for --after argument.")
            exit(1)
    else:
        if os.path.exists(downloaded_file):
            # Set comparison_date to last day that a file was downloaded -1
            comparison_date = (datetime.fromtimestamp(os.path.getmtime(downloaded_file)) - timedelta(days=1)).isoformat()
        else:
            comparison_date = date(1, 1, 1).isoformat() # download from alltime

    if not os.path.exists(downloaded_file): # Create the file if it doesn't exist
        with open(downloaded_file, 'w') as file:
            pass

    print(f'Downloading new content using date: {comparison_date}')
    new_links = get_new_tracks_and_releases(download_file, downloaded_file, comparison_date, args.replace)
    for link in new_links:
        print(f'found {link}')
        subprocess.run(['/srv/scripts/spotdl', 'download', link, '--output', '/srv/jellyfin/media/music/_{artist}_/_{album}_{year}_/{disc-number}_{disc-count}_{title}.mp3'])
