"""Download and extract MTGJSON deck files."""

import os
import zipfile
import requests
from pathlib import Path


class PreconDownloader:
    """Download and manage MTGJSON deck files."""

    DECK_URL = "https://mtgjson.com/api/v5/AllDeckFiles.zip"

    def __init__(self, data_dir: str = "data"):
        """Initialize downloader with data directory."""
        self.data_dir = Path(data_dir)
        self.deck_dir = self.data_dir / "decks"
        self.zip_path = self.data_dir / "AllDeckFiles.zip"

        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download(self) -> Path:
        """Download AllDeckFiles.zip if not present."""
        if self.zip_path.exists():
            print(f"✓ {self.zip_path.name} already exists, skipping download")
            return self.zip_path

        print(f"Downloading {self.zip_path.name}...")

        response = requests.get(self.DECK_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(self.zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end='')

        print(f"\n✓ Downloaded {self.zip_path.name}")
        return self.zip_path

    def extract(self) -> Path:
        """Extract deck files from zip."""
        if self.deck_dir.exists() and any(self.deck_dir.iterdir()):
            print(f"✓ Decks already extracted to {self.deck_dir}")
            return self.deck_dir

        if not self.zip_path.exists():
            self.download()

        print(f"Extracting to {self.deck_dir}...")
        self.deck_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.deck_dir)

        print(f"✓ Extracted deck files")
        return self.deck_dir

    def download_and_extract(self) -> Path:
        """Download and extract deck files."""
        self.download()
        return self.extract()
