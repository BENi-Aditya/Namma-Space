"""Release assets must reproduce local bytes without relying on ignored files."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('release_assets',Path(__file__).resolve().parents[1]/'scripts/release_assets.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.app=self.root/'apps/viewer';self.app.mkdir(parents=True)
        self.asset=self.app/'models/room/model.ply';self.asset.parent.mkdir(parents=True)
        self.payload=b'ply\nend_header\n'+bytes(range(256))*100
        self.asset.write_bytes(self.payload)
        (self.app/'models.json').write_text(json.dumps({'models':[{'id':'room','pointcloud':'models/room/model.ply'}]}))
    def tearDown(self):self.temp.cleanup()
    def test_snapshot_restores_exact_bytes_and_reuses_unchanged_chunks(self):
        release.snapshot(self.root)
        index=self.root/'deployment/assets/index.json';before=index.read_bytes()
        release.snapshot(self.root);self.assertEqual(index.read_bytes(),before)
        self.asset.unlink();release.restore(self.root)
        self.assertEqual(self.asset.read_bytes(),self.payload)
    def test_missing_new_asset_blocks_release(self):
        self.asset.unlink()
        with self.assertRaises(ValueError):release.snapshot(self.root)
    def test_corrupt_chunk_does_not_install_bad_asset(self):
        release.snapshot(self.root);self.asset.unlink()
        part=next((self.root/'deployment/assets/chunks').iterdir());part.write_bytes(b'corrupt')
        with self.assertRaises(OSError):release.restore(self.root)
        self.assertFalse(self.asset.exists())
if __name__=='__main__':unittest.main()
