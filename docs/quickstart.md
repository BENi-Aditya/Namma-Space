# Quickstart

The supported app is now a static viewer. Follow [the current reproduction guide](REPRODUCTION.md) for exact commands, artifact requirements, Mac MPS limitations and portable hosting. Historical setup commands and architecture plans are retained under history and are not current acceptance evidence.

```bash
./start-viewer.sh
python3 -m unittest discover -s test -v
python3 scripts/check_project.py
```
