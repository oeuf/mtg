"""Download MTGJSON data files."""

import requests
import os


class MTGJSONDownloader:
    """Download and manage MTGJSON data files."""

    BASE_URL = "https://mtgjson.com/api/v5"
    DATA_DIR = "data/raw"

    FILES = {
        "atomic_cards": "AtomicCards.json",
        "keywords": "Keywords.json",
        "related_cards": "RelatedCards.json"
    }

    @classmethod
    def download_all(cls):
        """Download all required MTGJSON files."""
        os.makedirs(cls.DATA_DIR, exist_ok=True)

        filepaths = {}

        for key, filename in cls.FILES.items():
            filepath = cls.download_file(filename)
            filepaths[key] = filepath

        return filepaths

    @classmethod
    def download_file(cls, filename: str) -> str:
        """Download a single MTGJSON file with progress."""
        url = f"{cls.BASE_URL}/{filename}"
        filepath = os.path.join(cls.DATA_DIR, filename)

        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"✓ {filename} already exists, skipping download")
            return filepath

        print(f"Downloading {filename}...")

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                # Progress indicator
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end='')

        print(f"\n✓ Downloaded {filename}")
        return filepath
