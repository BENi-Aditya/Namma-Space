#!/usr/bin/env python3
"""Local viewer server. Never terminates a process to claim its port."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'apps/viewer'))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as error:
        parser.exit(1, f'Cannot serve port {args.port}: {error}. Choose --port 8081. No process was stopped.\n')
    print(f'Namma Space: http://127.0.0.1:{args.port}/', flush=True)
    print('Local preview only. Public HTTPS deployment is required for submission.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
