"""Keep the world on the Hugging Face Hub, for hosts whose disks do not last.

A free Space's filesystem is wiped when it restarts. With `HF_TOKEN` and
`HF_REPO` set, the server pulls the saved world from a dataset repository
on start and pushes it back after it saves, no more often than
`HF_SYNC_SECONDS` apart, in a background thread so the world never waits.
Needs the `huggingface_hub` package, which the Dockerfile installs; a
plain local run never imports it.
"""
from __future__ import annotations

import os
import threading
import time
from pathlib import Path


class HubSync:
    def __init__(self, state_dir: Path, log=print) -> None:
        self.token = os.environ.get("HF_TOKEN", "")
        self.repo = os.environ.get("HF_REPO", "")
        self.every = float(os.environ.get("HF_SYNC_SECONDS", "120"))
        self.state_dir = state_dir
        self.log = log
        self.enabled = bool(self.token and self.repo)
        self.last = 0.0
        self.pending = False
        self.lock = threading.Lock()
        self.api = None
        if self.enabled:
            from huggingface_hub import HfApi  # installed in the image only
            self.api = HfApi(token=self.token)

    def pull(self) -> bool:
        """Fetch the saved world, if the repository has one."""
        if not self.enabled:
            return False
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import RepositoryNotFoundError
        try:
            self.api.create_repo(self.repo, repo_type="dataset", private=True, exist_ok=True)
            snapshot_download(self.repo, repo_type="dataset", local_dir=str(self.state_dir), token=self.token)
            self.log(f"pulled the world from {self.repo}")
            return (self.state_dir / "world.json").exists()
        except RepositoryNotFoundError:
            return False
        except Exception as e:  # noqa: BLE001 - the world must start regardless
            self.log(f"could not pull from the hub: {e}")
            return False

    def push_soon(self, message: str) -> None:
        """Push after the save, in the background, not too often."""
        if not self.enabled:
            return
        with self.lock:
            self.pending = True
            if time.monotonic() - self.last < self.every:
                return
            self.last = time.monotonic()
            self.pending = False
        threading.Thread(target=self.push, args=(message,), daemon=True).start()

    def push(self, message: str) -> None:
        if not self.enabled:
            return
        try:
            self.api.upload_folder(folder_path=str(self.state_dir), repo_id=self.repo, repo_type="dataset",
                                   commit_message=message, ignore_patterns=["*.log", ".cache/*"])
        except Exception as e:  # noqa: BLE001
            self.log(f"could not push to the hub: {e}")

    def flush(self) -> None:
        """Push now, waiting for it; for shutdown."""
        if self.enabled:
            self.push("shutdown")
