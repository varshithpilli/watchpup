# VTOP Marks Watchdog

A small Python watchdog script for VTOP data changes. Currently implemented only to fetch from the Marks endpoint.

> NOTE: This script currently depends on an active VTOP web session. When your session expires, you must refresh:
> - VTOP_JSESSIONID
> - VTOP_CSRF

## Features

- Periodically requests the VTOP marks endpoint
- Converts HTML response into structured JSON
- Stores the previous snapshot locally
- Detects changes using a hash-based comparison

Install dependencies:
```
pip install -r requirements.txt
```

TODO:
 - [ ] automatic cookie fetching
 - [ ] notifying the user
 - [ ] maybe make an exe