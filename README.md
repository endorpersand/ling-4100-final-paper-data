# LING 4100 Final Paper Data Collection

This is a repository for the data collection & processing steps of my term paper for LING 4100, "Analyzing Differences in Typographical Errors Between Physical and Touchscreen Keyboards."

This repository consists of 3 components: `data` (collected data), `processing` (data processing), `site` (data collection).

## Collecting Data

To collect data on typographical errors, this repository uses a fork of the monkeytypegame/monkeytype.

This forked version of `monkeytype` deletes all settings irrelevant to the data collection process, all backend code, and adds a new `Export words history` that creates a JSON file holding the results of a test.

To run the forked website (instructions for macOS/Linux, but Windows will be similar):

1. `cd site`
2. `npm install`
3. `npm run dev-fe`

To allow a mobile device on the same network to access this deployed site, create a new file `frontend/.env` that specifies a `BACKEND_URL` flag. It doesn't really matter what this URL is because it's not used in this fork.

## Processing Data

The data is processed (identifying typos and creating figures) with Python. Install Python, then:

1. `pip install -r processing/requirements.txt`
2. `python3 main.py`
