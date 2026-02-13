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

## How to use

You can run **VTOP WatchPup** in two different ways.

### 1. Using the windows exe - local compute (not yet implemented)
**Steps**
1. Go to the repository **Releases** page and download the latest executable package.
2. Extract the downloaded archive.
3. Inside the extracted folder, create the `.env` file
4. Open the provided `.env.example` file and copy its contents into the newly created `.env` file.
5. Fill in all required values in `.env` by following the examples in `.env.example`.
6. Run the executable once to verify that it starts correctly (raise an issue if it doesn't).
7. Add the executable to your system’s background/startup processes so that it keeps running automatically.

### 2. Using GH Actions (suggested)
**Steps**
1. Clone this repository to your own GitHub account (MIT ikr).
2. Open "your" repo and go to `Settings → Secrets and variables → Actions → Secrets`
3. Create new repository secrets for all required variables by referring to the `.env.example` file:
    - `REGD`
    - `PASS`
    - `VTOP_SEMID`
    - `INTERVAL_SECONDS`
    - `MAX_RETIRES`
    - `TG_BOT_TOKEN`
    - `TG_CHAT_ID`
5. You can start it manually from the **Actions** tab using the *workflow_dispatch* trigger, or let it run automatically based on the configured schedule.

### If you want to build it urself
1. Clone
2. Dependencies: `pip install -r requirements.txt`
3. env variables: `.env`
```.env.example
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
 - [ ] send the sub name instead of sub code
 - [ ] maybe make an exe
 - [ ] something so the user doesnt have to run get_semid
 - [ ] error handlers