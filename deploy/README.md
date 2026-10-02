# Keeping the world running somewhere

The world runs inside `serve.py` for as long as that process runs and
saves itself at the end of every generation. To keep it running when no
machine of yours is on, put it on a small server. Three ways, from least
to most hands-on.

## Fly.io (one small machine, a few dollars a month)

    deploy/fly.sh my-world ams

With `FLY_API_TOKEN` in the environment, that creates the app, a 1 GB
volume for the world, a steering token, and deploys. The page is then at
`https://my-world.fly.dev`. Anyone with the link can watch; the page asks
for the token once before it lets you steer (pause, speed, teachers, say,
new world) and remembers it in that browser.

The image is built on Fly's side, so no Docker is needed where you run
the script. `flyctl` is needed: https://fly.io/docs/flyctl/install/

To change the world's defaults for a fresh start, edit `[env]` in
`fly.toml` (`WORLD_LAW`, `WORLD_BEINGS`, `WORLD_SPEED`) or begin a new
world from the page.

## Any server with Docker

    docker compose up -d

Set `WORLD_TOKEN` in `docker-compose.yml` before exposing port 8000 to the
internet. The world lives in the `world_data` volume.

## Any server with Python

    WORLD_HOST=0.0.0.0 WORLD_TOKEN=choose-a-long-secret python serve.py --state /var/lib/world/world.json

A systemd unit that restarts it on failure:

    [Unit]
    Description=the world
    After=network.target
    [Service]
    WorkingDirectory=/opt/world
    Environment=WORLD_HOST=0.0.0.0 WORLD_TOKEN=choose-a-long-secret WORLD_STATE=/var/lib/world/world.json
    ExecStart=/usr/bin/python3 serve.py
    Restart=always
    [Install]
    WantedBy=multi-user.target

## What an endless run keeps and what it lets go

- The world's record keeps every birth, death, shell and contact; entries
  older than the newest three thousand move to `record.jsonl` beside the
  save file, append-only, chain intact.
- The sealed ledgers of the dead are kept for the newest two thousand; the
  record keeps every death with the final hash of its chain.
- A channel carries at most 1500 lived experiences and 200 featureless
  ones; the oldest go first, so a lineage stays quick. The ledger never
  forgets; the channel is what the mind works with.
