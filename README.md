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

### 1. Using the windows exe - local compute
**Steps**
1. Go to the repository **Releases** page and download the latest executable (watchdog.zip).
2. Extract the downloaded archive.
3. Inside the extracted folder, create the `.env` file
4. Open the provided `.env.example` file and copy its contents into the newly created `.env` file.
5. Fill in all required values in `.env` by following the examples in `.env.example`.
6. Run the `helper.exe` first and get the sem id of your choice and paste it in the `.env` (you can change the sem id whenever you want to change the focus of your watchdog)
7. Run the `watchpup.exe` (raise an issue if it doesn't work as intended).
7. Add the `watchpup.exe` to your system’s background/startup processes so that it keeps running automatically (or whatever).

### 2. Using GH Actions (suggested)
**Steps**
1. Clone this repository to your own GitHub account (MIT ikr. No forking cuz gh doesnt allow cron jobs to run in forked repos).
2. Open "your" repo and go to `Settings -> Secrets and variables -> Actions -> Secrets`
3. Create new repository secrets for all required variables by referring to the `.env.example` file:
    - `REGD`
    - `PASS`
    - `VTOP_SEMID`
    - `INTERVAL_SECONDS`
    - `MAX_RETIRES`
    - `TG_BOT_TOKEN`
    - `TG_CHAT_ID`
5. make the `.github/workflows/main.yml` file and paste the following in it and push it to "your" repo again.

```
name: Watchdog job

on:
  schedule:
    - cron: "*/30 * * * *" 
    # - cron: "*/mins */hours * * *"
    # the above is an example for quick config
    # refer the gh actions cron docs to make your own scheduling (mine runs every 30 mins)
  workflow_dispatch:

jobs:
  watchdog:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run watchdog
        env:
          GH_ACTIONS: "true"
          REGD: ${{ secrets.REGD }}
          PASS: ${{ secrets.PASS }}
          VTOP_SEMID: ${{ secrets.VTOP_SEMID }}
          MAX_RETIRES: ${{ secrets.MAX_RETIRES }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
          TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
        run: python main.py

      - name: Commit updated state
        run: |
          git config user.name "watchpup-bot"
          git config user.email "bot@watchpup"
          git add state/last_saved.json
          git diff --quiet && git diff --staged --quiet || git commit -m "bot: update state"
          git push
```

> Note: Actions implementation saves the last state by commiting it back to the repository, so if you're insecure abt ur marks or smtg, make the repo private but also keep in mind the 2000 minutes limit on actions' private repo.

### If you want to build it urself
1. Clone
2. Dependencies: `pip install -r requirements.txt`
3. env variables: `.env`
```.env.example
REGD=xxxxxxxxxxxx
PASS=xxxxxxxxxxxx

INTERVAL_SECONDS =xxxxxxxxxxx # in seconds
MAX_RETIRES=10 # to skip the google captcha

TG_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxx
TG_CHAT_ID=xxxxxxxxxxxxxxxxxxxx

VTOP_SEMID=xxxxxxxxxxxxxx
```
You could get the `VTOP_SEMID` from the list by running get_semid.py

TODO:
 - [X] show actual change in the data
 - [X] logging
 - [X] automatic cookie fetching (gotta deal with captcha)
 - [X] notifying the user
 - [X] automatic sem id maybe
 - [X] extend to more than just the marks page (~~grades~~, ~~cgpa~~, ~~calendar~~)
 - [X] maybe make an exe
 - [X] something so the user doesnt have to run get_semid
 - [ ] send the sub name instead of sub code
 - [ ] error handlers

## Credits
Insights into VTop auth:  **[VIT Verse app](https://github.com/vit-verse/vitverse-app)** by *[Divyanshu Patel](https://github.com/divyanshupatel17)*
Captcha weights: **[VtopCaptchaSolver3.0](https://github.com/pratyush3124/VtopCaptchaSolver3.0)** by *[Pratyush](https://github.com/pratyush3124)*