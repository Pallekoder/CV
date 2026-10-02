#!/usr/bin/env python3
"""Put the world on a free Hugging Face Space, from anywhere with a token.

    HF_TOKEN=... python deploy/space.py <hf-username> [space-name]

Creates a Docker Space, a private dataset repository where the world keeps
itself, the Space's secrets (a steering token it generates and prints, and
the hub token for saving) and variables, and uploads this repository to the
Space. Needs `pip install huggingface_hub`. The Space builds and starts on
its own; the page is at https://huggingface.co/spaces/<user>/<space>.
"""
from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

from huggingface_hub import HfApi

HERE = Path(__file__).resolve().parent.parent


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    user = argv[1]
    name = argv[2] if len(argv) > 2 else "the-world"
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        print("HF_TOKEN is not set")
        return 2
    api = HfApi(token=token)
    space = f"{user}/{name}"
    dataset = f"{user}/{name}-state"

    api.create_repo(space, repo_type="space", space_sdk="docker", exist_ok=True)
    api.create_repo(dataset, repo_type="dataset", private=True, exist_ok=True)

    steering = os.environ.get("WORLD_TOKEN") or secrets.token_urlsafe(18)
    api.add_space_secret(space, "WORLD_TOKEN", steering)
    api.add_space_secret(space, "HF_TOKEN", token)
    api.add_space_variable(space, "HF_REPO", dataset)
    for key, default in (("WORLD_LAW", "corner"), ("WORLD_BEINGS", "12"), ("WORLD_SPEED", "4"), ("HF_SYNC_SECONDS", "120")):
        api.add_space_variable(space, key, os.environ.get(key, default))

    api.upload_folder(
        folder_path=str(HERE), repo_id=space, repo_type="space", commit_message="the world",
        ignore_patterns=[".git/*", "state/*", "__pycache__/*", "*.pyc", "tests/*", "*.png"],
    )
    print(f"the world is being built at https://huggingface.co/spaces/{space}")
    print(f"it keeps itself in https://huggingface.co/datasets/{dataset}")
    print(f"steering token (the page asks for it once): {steering}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
