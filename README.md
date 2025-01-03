![commit activity](https://img.shields.io/github/commit-activity/m/TheNewThinkTank/fitness-tracker)
![CI](https://github.com/TheNewThinkTank/fitness-tracker/actions/workflows/wf.yml/badge.svg)
[![GitHub repo size](https://img.shields.io/github/repo-size/TheNewThinkTank/fitness-tracker?style=flat&logo=github&logoColor=whitesmoke&label=Repo%20Size)](https://github.com/TheNewThinkTank/fitness-tracker/archive/refs/heads/main.zip)

[![Documentation Status](https://readthedocs.org/projects/fitness-tracker/badge/?version=latest)](https://fitness-tracker.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/TheNewThinkTank/Fitness-Tracker/branch/main/graph/badge.svg?token=CKAX4A3JQF)](https://codecov.io/gh/TheNewThinkTank/Fitness-Tracker)

# Fitness-Tracker

<p align="center">
  <img src="docs/project_docs/img/thumbnails/logo.png" width="400"/>
</p>

[Main Website](https://thenewthinktank.github.io/fitness-tracker/)

[Tech Docs](https://fitness-tracker.readthedocs.io/en/latest/index.html)

<!--
## Frontend setup

```BASH
mkdir frontend && cd frontend
npx degit sveltejs/template svelte-app
cd svelte-app
npm install

# Move the contents of the svelte-app directory to the frontend directory and remove the svelte-app directory
cd ..
mv svelte-app/* .
mv svelte-app/.* .
rmdir svelte-app

# Upgrade Svelte from "^3.55.0" to "^5.0.0"

# remove node_modules and package-lock.json:
rm -rf node_modules
rm package-lock.json
# Specify version "^5.0.0" for svelte in package.json
# manually bump of version for all dependencies as well.

npm install
npm list svelte
# test the app still works:
npm run dev
```
-->

## Running locally

```BASH
# docker-compose up --build

docker compose --profile ci up --build --attach-dependencies --remove-orphans

# then visit http://localhost:5000
```

Or, running without containers

```BASH
# Start the Backend
cd src
uvicorn main:app --reload

# Start the Frontend
cd frontend
npm run dev
```

**Debugging**:
from the url, open the browser's developer tools (`F12` or `Cmd+Shift+C`)

## Known issues

**Issue**: `zsh: command not found: docker-compose`

**solution**:

```BASH
sudo rm /usr/local/bin/docker-compose

sudo ln -s /Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose /usr/local/bin/docker-compose

# check version:
docker-compose version

# Output should be similar to:
Docker Compose version v2.29.1-desktop.1
```

## Testing endpoints locally

Overview of endpoints

- [root](http://127.0.0.1:8000/)
- [data](http://127.0.0.1:8000/data)
- [dates](http://127.0.0.1:8000/dates)
- [dates_and_splits](http://127.0.0.1:8000/dates_and_splits)
- [date](http://127.0.0.1:8000/dates/{date})
- [exercise](http://127.0.0.1:8000/{date}/exercises/{exercise})

## For contributors

[Project tracking](https://thenewthinktank.atlassian.net/jira/software/projects/FT/boards/2)
