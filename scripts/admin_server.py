#!/usr/bin/env python3
"""Loopback-only, persistent video training queue and viewer server."""
import fcntl
import argparse, atexit, json, os, re, secrets, shutil, signal, socket, subprocess, sys, threading, time, uuid, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'apps/viewer'
STATE = ROOT / 'namma-space-project/.work/admin'
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.RLock()
STOP = threading.Event()
PROCESS = None
JOBS = []
HISTORY = []
PRESETS = {'preview': 1000, 'balanced': 7000, 'quality': 15000}
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

def save(job):
    path = STATE / (job['id'] + '.json')
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(job, indent=2))
    temp.replace(path)

def python_path():
    candidates = [os.environ.get('NAMMA_PYTHON', ''), str(Path.home() / 'miniforge3/envs/namma-space/bin/python'), str(Path.home() / 'miniconda3/envs/namma-space/bin/python'), sys.executable]
    return next((p for p in candidates if p and Path(p).is_file()), sys.executable)

def environment():
    env = os.environ.copy()
    env['PATH'] = str(Path(python_path()).parent) + os.pathsep + env.get('PATH', '') + ':/opt/homebrew/bin:/usr/local/bin'
    env.update(NAMMA_PARENT_PID=str(os.getpid()), PYTHONUNBUFFERED='1', PYTORCH_ENABLE_MPS_FALLBACK='1', MPLCONFIGDIR=str(STATE / 'matplotlib'))
    return env

def models():
    data = json.loads((APP / 'models.json').read_text())
    for m in data['models']:
        key = {'gaussian':'splat', 'pointcloud':'pointcloud', 'stl':'stl'}.get(m.get('defaultAsset'), 'pointcloud')
        m['ready'] = bool(m.get(key) and (APP / m[key]).is_file())
    return data

def history():
    results = []
    work = ROOT / 'namma-space-project/.work'
    for config in work.glob('**/config.yml'):
        if any(j['model_id'] in config.parts for j in JOBS):
            continue
        checkpoints = list(config.parent.glob('nerfstudio_models/*.ckpt'))
        results.append({'id':str(config.relative_to(work)), 'name':config.parent.parent.parent.name, 'state':'Checkpoint saved' if checkpoints else 'No checkpoint found', 'checkpoints':len(checkpoints)})
    return results

def terminate():
    global PROCESS
    with LOCK:
        process = PROCESS
    if process and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

def worker():
    global PROCESS
    while not STOP.wait(.5):
        with LOCK:
            job = next((j for j in reversed(JOBS) if j['state']=='queued'), None)
            if not job: continue
            job.update(state='processing', started=time.time(), stage='processing')
            save(job)
        log_path = STATE / (job['id'] + '.log')
        try:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0)); port = sock.getsockname()[1]
            job['viewer_url'] = f'http://127.0.0.1:{port}'
            command = [python_path(), '-u', str(ROOT/'scripts/pipeline/reconstruct.py'), job['video'], job['model_id'], '--iterations', str(job['iterations']), '--method', 'nerfacto', '--device', 'mps' if sys.platform=='darwin' else 'cuda', '--viewer-port', str(port), '--execute']
            with log_path.open('w') as log:
                with LOCK:
                    if job['state']=='cancelled': continue
                    PROCESS = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=environment(), cwd=ROOT, start_new_session=True)
                    job['pid'] = PROCESS.pid
                    save(job)
                for raw in PROCESS.stdout:
                    line = ANSI.sub('',raw)
                    log.write(line); log.flush()
                    with LOCK:
                        if line.startswith('NAMMA_STAGE '):
                            job['stage'] = line.strip().split()[-1]
                            job['stage_started'] = time.time()
                        if 'Viewer running locally at:' in line or ('HTTP' in line and job['viewer_url'] in line): job['viewer_ready'] = True
                        match = re.search(r'(\d+)\s+\(([\d.]+)%\)', line)
                        if match and job.get('stage')=='training':
                            step = int(match[1]); job['step'] = step
                            job['percent'] = min(100, 100*step/job['iterations'])
                            elapsed = time.time()-job.get('stage_started', time.time())
                            if step > 10: job['eta_seconds'] = round(elapsed / step * max(0,job['iterations']-step))
                        save(job)
                code = PROCESS.wait()
            with LOCK:
                if job['state'] != 'cancelled':
                    job['state'] = 'completed' if code==0 else 'failed'
                    if code: job['error'] = 'Pipeline stopped. Inspect the log below; your input and partial results are preserved.'
                job['finished'] = time.time(); job['viewer_ready'] = False
                if code==0 and job['state']=='completed': rename(job['model_id'], job['name'])
                save(job)
        except Exception as exc:
            with LOCK:
                job.update(state='failed', error=str(exc)); save(job)
        finally:
            with LOCK: PROCESS = None

def rename(model_id, name):
    with (APP / 'models.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _rename(model_id, name)

def _rename(model_id, name):
    if not isinstance(name,str) or not 1 <= len(name.strip()) <= 100: raise ValueError('Name must be 1–100 characters.')
    path = APP / 'models.json'
    data = json.loads(path.read_text())
    model = next((m for m in data['models'] if m['id']==model_id), None)
    if model is None: raise ValueError('Model not found.')
    model['name'] = name.strip()
    temp = path.with_suffix('.admin.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)

def save_view(model_id, state):
    if not isinstance(state, dict) or state.get('modelId') != model_id:
        raise ValueError('View must belong to this model')
    import math
    def finite(value):
        return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)
    for field in ['position', 'rotation']:
        if not isinstance(state.get(field), dict) or not all(finite(state[field].get(k)) for k in 'xyz'):
            raise ValueError('Invalid model transform')
    if not finite(state.get('scale')) or state['scale'] <= 0: raise ValueError('Invalid scale')
    camera = state.get('camera', {})
    for field, size in [('position',3), ('quaternion',4), ('target',3)]:
        values = camera.get(field)
        if not isinstance(values,list) or len(values)!=size or not all(finite(v) for v in values):
            raise ValueError('Invalid camera')
    for field in ['fov','near','far','zoom']:
        if not finite(camera.get(field)) or camera[field]<=0: raise ValueError('Invalid camera projection')
    if camera['near']>=camera['far'] or camera['fov']>=180: raise ValueError('Invalid camera range')
    crop = state.get('crop', {})
    for field in ['xMin','xMax','yMin','yMax','zMin','zMax']:
        try: value = float(crop[field])
        except (KeyError,TypeError,ValueError): raise ValueError('Invalid crop')
        if not math.isfinite(value) or not 0<=value<=100: raise ValueError('Invalid crop')
    if state.get('assetType') not in ['gaussian','pointcloud','stl','ply']: raise ValueError('Invalid asset')
    with (APP/'models.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path = APP/'models.json'
        data = json.loads(path.read_text())
        model = next((m for m in data['models'] if m['id']==model_id),None)
        if model is None: raise ValueError('Unknown model')
        model['viewState'] = state
        temp = path.with_suffix('.view.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(APP),**kwargs)
    def log_message(self,*args): pass
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def answer(self,data,status=200):
        body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def valid_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def do_GET(self):
        if not self.valid_host(): return self.answer({'error':'Local access only'},403)
        url=urlparse(self.path)
        if url.path=='/api/status':
            with LOCK: return self.answer({'token':TOKEN,'jobs':JOBS,'history':HISTORY,'presets':PRESETS})
        if url.path=='/api/models': return self.answer(models())
        if url.path.startswith('/api/log/'):
            ident=url.path.split('/')[-1]
            if not re.fullmatch('[a-f0-9]{32}',ident): return self.answer({'error':'Unknown log'},404)
            try: offset=max(0,int(parse_qs(url.query).get('offset',['0'])[0]))
            except ValueError: return self.answer({'error':'Invalid log offset'},400)
            path=STATE/(ident+'.log')
            if not path.exists(): return self.answer({'text':'','offset':0})
            with path.open('rb') as stream:
                stream.seek(offset);data=stream.read(128*1024)
                return self.answer({'text':data.decode(errors='replace'),'offset':stream.tell()})
        if url.path=='/admin': self.path='/admin.html'
        super().do_GET()
    def do_POST(self):
        if not self.valid_host() or self.headers.get('X-Namma-Token')!=TOKEN:
            return self.answer({'error':'Refresh this local page before trying again.'},403)
        url=urlparse(self.path)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if url.path=='/api/upload':
                query=parse_qs(url.query);preset=query.get('preset',['balanced'])[0]
                if preset not in PRESETS: raise ValueError('Unknown preset')
                if length<=0 or length>20*1024**3: raise ValueError('Choose a video smaller than 20 GB.')
                if shutil.disk_usage(STATE).free < length+5*1024**3: raise ValueError('Free more disk space: upload plus at least 5 GB is required.')
                missing=[x for x in ['ns-process-data','ns-train','ns-export','colmap','ffmpeg','ffprobe'] if not shutil.which(x,path=environment()['PATH'])]
                if missing: raise ValueError('Missing training tools: '+', '.join(missing))
                ident=uuid.uuid4().hex
                suffix=Path(query.get('filename',['video.mp4'])[0]).suffix.lower()
                if suffix not in ['.mp4','.mov','.mkv','.avi','.webm','.m4v']: raise ValueError('Unsupported video extension')
                path=STATE/(ident+suffix)
                try:
                    self.connection.settimeout(120)
                    with path.open('xb') as output:
                        remaining=length
                        while remaining:
                            chunk=self.rfile.read(min(1024*1024,remaining))
                            if not chunk: raise ValueError('Upload interrupted')
                            output.write(chunk);remaining-=len(chunk)
                    probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_type','-of','json',str(path)],capture_output=True,text=True,timeout=30,env=environment())
                    if probe.returncode or not json.loads(probe.stdout).get('streams'): raise ValueError('File has no readable video stream')
                except Exception:
                    path.unlink(missing_ok=True);raise
                name=query.get('name',[Path(query.get('filename',['New model'])[0]).stem])[0].strip()[:100] or 'New model'
                job={'id':ident,'model_id':'capture-'+ident[:12],'name':name,'video':str(path),'state':'queued','stage':'queued','iterations':PRESETS[preset],'preset':preset,'created':time.time()}
                with LOCK: JOBS.insert(0,job);save(job)
                return self.answer(job,201)
            if length>16384: raise ValueError('Request too large')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise ValueError('Expected a JSON object')
            with LOCK:
                if url.path=='/api/view-state': save_view(body['id'],body['state'])
                elif url.path=='/api/rename': rename(body['id'],body['name'])
                elif url.path=='/api/cancel':
                    job=next(j for j in JOBS if j['id']==body['id'])
                    if job['state'] not in ['queued','processing']: raise ValueError('This run is already stopped')
                    active=job['state']=='processing';job['state']='cancelled';save(job)
                else: return self.answer({'error':'Unknown endpoint'},404)
            if url.path=='/api/cancel' and active: terminate()
            return self.answer({'ok':True})
        except (ValueError, KeyError, StopIteration, OSError, subprocess.TimeoutExpired) as exc:
            self.answer({'error':str(exc) or 'Unknown run'},400)

def main():
    global HISTORY
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8080);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    STATE.mkdir(parents=True,exist_ok=True)
    import fcntl
    lockfile=(STATE/'server.lock').open('w')
    try: fcntl.flock(lockfile,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('Another training dashboard is already running.')
    for path in STATE.glob('*.json'):
        job=json.loads(path.read_text())
        if job['state'] in ['processing','queued']:
            job.update(state='interrupted',error='Dashboard stopped before completion. Partial results are preserved.');save(job)
        JOBS.append(job)
    JOBS.sort(key=lambda j:j['created'],reverse=True)
    HISTORY=history()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    threading.Thread(target=worker,daemon=True).start()
    def shutdown(): STOP.set();terminate()
    atexit.register(shutdown)
    signal.signal(signal.SIGTERM,lambda *_:sys.exit(0))
    print(f'Namma Space dashboard: http://127.0.0.1:{args.port}/admin',flush=True)
    if not args.no_browser: webbrowser.open(f'http://127.0.0.1:{args.port}/admin')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: shutdown();server.server_close()
if __name__=='__main__': main()
