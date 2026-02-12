# VTOP WatchPup

A small Python watchdog script for VTOP data changes. Currently implemented only to fetch from the Marks endpoint.

<!-- > NOTE: This script currently depends on an active VTOP web session. When your session expires, you must refresh:
> - VTOP_JSESSIONID
> - VTOP_CSRF
> - VTOP_SERVERID -->

## Features

- Periodically requests the VTOP marks endpoint
- Converts HTML response into structured JSON
- Stores the previous snapshot locally
- Detects changes using a hash-based comparison

Install dependencies:
```
pip install -r requirements.txt
```

env variables:
```
REGD=xxxxxxxxxxxx
PASS=xxxxxxxxxxxx

VTOP_SEMID=xxxxxxxxxxxxxx
INTERVAL_SECONDS =xxxxxxxxxxx # in seconds
MAX_RETIRES=10 # to skip the google captcha

TG_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxx
TG_CHAT_ID=xxxxxxxxxxxxxxxxxxxx
```
You could get the `VTOP_SEMID` from the list by running get_semid.py

TODO:
 - [X] show actual change in the data
 - [X] logging
 - [X] automatic cookie fetching (gotta deal with captcha)
 - [X] notifying the user
 - [X] automatic sem id maybe
 - [X] extend to more than just the marks page (~~grades~~, ~~cgpa~~, ~~calendar~~)
 - [ ] error handlers
 - [ ] maybe make an exe