"""Regression checks for data preservation and the supported export integration."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reconstruct', ROOT / 'scripts/pipeline/reconstruct.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def test_rejects_missing_images_and_nonfinite_poses(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            identity = [[int(i == j) for j in range(4)] for i in range(4)]
            frame = {'file_path': 'frame.png', 'transform_matrix': identity}
            poses = directory / 'transforms.json'
            poses.write_text(json.dumps({'frames': [frame] * 20}))
            with self.assertRaisesRegex(ValueError, 'Missing'):
                pipeline.validate_poses(directory)
            (directory / 'frame.png').touch()
            self.assertEqual(pipeline.validate_poses(directory), 20)
            identity[0][0] = float('nan')
            poses.write_text(json.dumps({'frames': [frame] * 20}))
            with self.assertRaisesRegex(ValueError, 'Non-finite'):
                pipeline.validate_poses(directory)

    def test_registration_preserves_other_models_and_rejects_pointcloud(self):
        with tempfile.TemporaryDirectory() as temp:
            viewer = Path(temp)
            manifest = viewer / 'models.json'
            manifest.write_text(json.dumps({'models': [{'id': 'existing'}], 'latest': 'existing'}))
            ply = viewer / 'splat.ply'
            ply.write_bytes(b'ply\nproperty float x\nend_header\n')
            with self.assertRaisesRegex(ValueError, 'Gaussian'):
                pipeline.register_model(viewer, 'new', ply)
            self.assertEqual(json.loads(manifest.read_text())['latest'], 'existing')
            ply.write_bytes(b'ply\nproperty float x\nproperty float opacity\nproperty float scale_0\nproperty float rot_0\nend_header\n')
            pipeline.register_model(viewer, 'new', ply)
            data = json.loads(manifest.read_text())
            self.assertEqual([m['id'] for m in data['models']], ['new', 'existing'])
            self.assertEqual(data['latest'], 'new')

    def test_live_pipeline_orders_stages_and_registers_only_after_export(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); work = root / 'work'; work.mkdir()
            viewer = root / 'viewer'; viewer.mkdir()
            (viewer / 'models.json').write_text('{"models":[],"latest":null}')
            video = root / 'input.mp4'; video.write_bytes(b'test fixture')
            calls = []
            def run(command, **kwargs):
                calls.append(command)
                if command[0] == 'ns-process-data':
                    output = Path(command[command.index('--output-dir')+1])
                    (output / 'frame.png').touch()
                    matrix = [[int(i==j) for j in range(4)] for i in range(4)]
                    (output / 'transforms.json').write_text(json.dumps({'frames':[{'file_path':'frame.png','transform_matrix':matrix}]*20}))
                elif command[0] == 'ns-train':
                    output = Path(command[command.index('--output-dir')+1]); output.mkdir()
                    (output / 'config.yml').write_text('test fixture')
                    self.assertIn('--viewer.quit-on-train-completion', command)
                    self.assertIn('viewer+tensorboard', command)
                elif 'pointcloud' in command:
                    self.assertEqual(json.loads((viewer/'models.json').read_text())['models'], [])
                    output = Path(command[command.index('--output-dir')+1]); output.mkdir(parents=True)
                    (output/'point_cloud.ply').write_bytes(b'ply\nproperty float x\nproperty float y\nproperty float z\nend_header\n')
                return subprocess.CompletedProcess(command,0)
            with patch.object(pipeline,'WORK',work), patch.object(pipeline,'VIEWER',viewer), patch.object(pipeline.shutil,'which',return_value='/tool'), patch.object(pipeline.subprocess,'run',side_effect=run):
                pipeline.run_pipeline(video,'fresh',100,True,'nerfacto','mps',7017)
            self.assertEqual(len(calls),4)
            self.assertEqual(json.loads((viewer/'models.json').read_text())['latest'],'fresh')
            self.assertEqual(json.loads((work/'fresh/run.json').read_text())['registered_frames'],20)

    def test_existing_run_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / 'existing').mkdir()
            video = work / 'input.mov'
            video.touch()
            with patch.object(pipeline, 'WORK', work), self.assertRaisesRegex(ValueError, 'already exists'):
                pipeline.run_pipeline(video, 'existing', 10)
            self.assertTrue((work / 'existing').is_dir())

    def test_failed_export_never_changes_manifest(self):
        # A successful trainer is insufficient: export must exist and be valid before registration.
        with tempfile.TemporaryDirectory() as temp:
            viewer = Path(temp)
            (viewer / 'models.json').write_text('{"models":[],"latest":null}')
            before = (viewer / 'models.json').read_bytes()
            with self.assertRaises(FileNotFoundError):
                pipeline.register_model(viewer, 'new', viewer / 'missing.ply')
            self.assertEqual((viewer / 'models.json').read_bytes(), before)

    def test_nerf_pointcloud_accepts_double_coordinates_without_claiming_splats(self):
        with tempfile.TemporaryDirectory() as temp:
            viewer = Path(temp)
            (viewer / 'models.json').write_text('{"models":[],"latest":null}')
            ply = viewer / 'point_cloud.ply'
            ply.write_bytes(b'ply\nproperty double x\nproperty double y\nproperty double z\nend_header\n')
            pipeline.register_model(viewer, 'mac', ply, 'nerfacto')
            entry = json.loads((viewer / 'models.json').read_text())['models'][0]
            self.assertEqual(entry['defaultAsset'], 'pointcloud')
            self.assertNotIn('splat', entry)


if __name__ == '__main__':
    unittest.main()
