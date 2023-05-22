import os
from dotenv import load_dotenv
from pathlib import Path
import requests
from datetime import datetime
from getpass import getpass
from alive_progress import alive_bar
from ratelimit import limits, sleep_and_retry

BASE_URL = "https://api.mangadex.org"
load_dotenv(Path("auth.env"))
REFRESH_TOKEN=os.environ.get('refresh_token')

# Ratelimit on MangaDex is 5 calls per second
# Grabbed ratelimit code from: https://stackoverflow.com/a/64845203
CALLS = 5
RATE_LIMIT = 1

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    ''' Empty function just to check for calls to API '''
    return

"""
Login to Mangadex / Refresh session
Session expires after 15 min, Refresh token lasts for a month
@param creds: dict with username/password
@return (session_token, expires, refresh_token)
"""
def login(creds={}):
    if REFRESH_TOKEN:
        refresh_token = REFRESH_TOKEN
        r = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"token": refresh_token},
        )
        session_token = r.json()["token"]["session"]
        expires = datetime.now().timestamp() + 15 * 60000
        return (session_token, expires, refresh_token)
    
    r = requests.post(
        f"{BASE_URL}/auth/login", 
        json=creds
    )
    r_json = r.json()

    session_token = r_json["token"]["session"]
    expires = datetime.now().timestamp() + 15 * 60000
    refresh_token = r_json["token"]["refresh"]

    print(f'{session_token}, \n {datetime.utcfromtimestamp(int(expires)).strftime("%Y-%m-%d %H:%M:%S")}, \n refresh: {refresh_token}')
    return (session_token, expires, refresh_token)

"""
Get the logged in user's (default list)
You can call /user/id/list to get a custom list but i'm not doing that here.
"""
def get_list(session_token):
    check_limit()
    r = requests.get(
        f'{BASE_URL}/user/list',
        headers={
            "Authorization": f"Bearer {session_token}"
        },
    )
    print(r.json())
    return r.json()

"""
Get the logged in user's follows
"""
def get_follows(session_token):
    check_limit()
    # Go through each offset
    r = requests.get(
        f'{BASE_URL}/user/follows/manga',
        headers={
            "Authorization": f"Bearer {session_token}"
        },
        params={
            'limit': 100
        }
    )
    print(r.json())
    return r.json()

"""
Get the logged-in user's manga and their statuses
"""
def get_all_manga_status(session_token):
    check_limit()
    # Go through each offset
    r = requests.get(
        f'{BASE_URL}/manga/status',
        headers={
            "Authorization": f"Bearer {session_token}"
        },
    )
    return r.json()

"""
Set the status of a manga
"""
def set_manga_status(session_token, manga_id, status):
    check_limit()
    # Go through each offset
    r = requests.post(
        f'{BASE_URL}/manga/{manga_id}/status',
        headers={
            "Authorization": f"Bearer {session_token}"
        },
        json={"status": status},
    )
    return r.json()

"""
Unfollow a manga with the given id.
"""
def unfollow_manga(session_token, manga_id):
    check_limit()
    r = requests.delete(
        f'{BASE_URL}/manga/{manga_id}/follow',
        headers={
            "Authorization": f"Bearer {session_token}"
        },
    )
    return r.json()

"""
Queries mangadex for all manga that a user has some sort of status on
if it's reading -> set to on hold
@param unfollow: defaults to false. if true, also unfollows all manga in list
"""
def set_all_manga_to_status(session_token, status, unfollow=False):
    manga_status_data = get_all_manga_status(session_token).get('statuses')
    print(f"Number of Manga in user\'s manga list: {len(manga_status_data)}")
    count = 0
    with alive_bar(len(manga_status_data.keys())) as bar:
        for manga in manga_status_data.keys():
            if manga_status_data.get(manga) == 'reading':
                set_manga_status(session_token, manga, status)
                count+=1
            if unfollow:
                unfollow_manga(session_token, manga)
            bar()
    print(f'Set {count} manga to status -> {status}')

def main():
    # Prompt user for username/password
    if not REFRESH_TOKEN:
        username = input('Username: ')
        password = getpass()
        creds = {
            "username": username,
            "password": password,
        }
        login_data = login(creds)
    login_data = login()
    set_all_manga_to_status(login_data[0], 'on_hold', unfollow=True)
    
    return

if __name__ == "__main__":
    main()