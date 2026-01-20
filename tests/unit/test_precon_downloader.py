"""Unit tests for precon downloader."""

import os
import tempfile
from src.data.precon_downloader import PreconDownloader


def test_precon_downloader_url():
    """Test that downloader has correct URL."""
    assert PreconDownloader.DECK_URL == "https://mtgjson.com/api/v5/AllDeckFiles.zip"


def test_precon_downloader_creates_directory():
    """Test that downloader creates data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PreconDownloader(data_dir=tmpdir)

        # Directory should exist
        assert os.path.exists(tmpdir)
        # Downloader should store paths
        assert downloader.data_dir.exists()
