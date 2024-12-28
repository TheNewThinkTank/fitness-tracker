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
```

## Running locally

```BASH
# docker-compose up --build

docker compose --profile ci up --build --attach-dependencies --remove-orphans

# then visit http://localhost:5000
```

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
