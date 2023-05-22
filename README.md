# MangaDex Quick Status Changer / Unfollower
A quick script to update my reading list to put everything into "On hold" and also unfollow everything so my feed is cleaner.

Calls the mangadex api: https://api.mangadex.org/docs/

Include your refresh token (refreshes once per month) in auth.env as "refresh_token" if you are going to call it more than once. 
Otherwise, the script will prompt you for your username/pass.

Example:

```
python mangadexupdate.py

Number of Manga in user's manga list: 466
|████████████████████████████████████████| 466/466 [100%] in 2:32.2 (3.06/s) 
Set 0 manga to status -> on_hold
```
