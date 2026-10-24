# Supported entry points

- `../start-viewer.sh [--port 8080]`: localhost static app preview.
- `pipeline/reconstruct.py VIDEO NEW_ID [--method nerfacto --device mps --iterations N]`: dry-run; `--execute` starts processing/training.
- `pipeline/process_video.sh`: wrapper for reconstruct.py.
- `check_project.py`: validate manifest, assets and supported source paths.
- `package_viewer.py [--output PATH]`: portable static bundle, refuses overwrite.
- `../test/test_pipeline.py`: non-destructive regression suite.

## Preserved legacy tools

setup/, training/, tests/ and all other pipeline scripts preserve experimental history. **Do not batch-run them.** Several contain rm -rf, shutil.rmtree, hard-coded local paths, config mutation, or GPU claims that were not verified. scripts/tests are historical diagnostics, not the safe test suite; some delete sparse reconstructions. Use test/ for supported tests. Legacy multi-format export_pipeline.py assumes NeRF pointclouds and may reuse a root cloud under a different model identity, so it is not the supported Gaussian export path. No legacy script was run during the audit. Root train-*.sh files are also preserved legacy presets.
