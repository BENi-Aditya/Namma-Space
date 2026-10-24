"""Isolated controller/API tests: no real model training or user data changes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import sys

spec=importlib.util.spec_from_file_location('admin',Path(__file__).resolve().parents[1]/'scripts/admin_server.py')
admin=importlib.util.module_from_spec(spec);spec.loader.exec_module(admin)

class AdminTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.app=self.root/'app';self.app.mkdir();self.state=self.root/'state';self.state.mkdir()
        (self.app/'models.json').write_text(json.dumps({'latest':'one','models':[{'id':'one','name':'Original','defaultAsset':'pointcloud','pointcloud':'models/one/point_cloud.ply'}]}))
        self.patches=[patch.object(admin,'APP',self.app),patch.object(admin,'STATE',self.state),patch.object(admin,'JOBS',[]),patch.object(admin,'HISTORY',[],create=True)]
        for p in self.patches:p.start()
        self.server=admin.ThreadingHTTPServer(('127.0.0.1',0),admin.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def request(self,path,body=None,token=True,headers=None):
        h=headers or {}
        if token:h['X-Namma-Token']=admin.TOKEN
        data=json.dumps(body).encode() if body is not None else None
        return urlopen(Request(self.url+path,data=data,headers=h))
    def test_rename_persists_and_keeps_asset_id(self):
        self.request('/api/rename',{'id':'one','name':'Living room'})
        m=json.loads((self.app/'models.json').read_text())['models'][0]
        self.assertEqual(m['name'],'Living room');self.assertEqual(m['id'],'one');self.assertEqual(m['pointcloud'],'models/one/point_cloud.ply')
    def test_mutations_require_token_and_local_host(self):
        with self.assertRaises(HTTPError) as error:self.request('/api/rename',{'id':'one','name':'bad'},token=False)
        self.assertEqual(error.exception.code,403);error.exception.close()
        with self.assertRaises(HTTPError) as error:self.request('/api/status',headers={'Host':'evil.example'})
        self.assertEqual(error.exception.code,403);error.exception.close()
    def test_missing_asset_not_ready(self):
        self.assertFalse(admin.models()['models'][0]['ready'])
    def test_cancel_queued_is_durable(self):
        job={'id':'a'*32,'state':'queued'};admin.JOBS.append(job)
        self.request('/api/cancel',{'id':job['id']})
        self.assertEqual(json.loads((self.state/(job['id']+'.json')).read_text())['state'],'cancelled')
    def test_upload_validates_video_and_queues(self):
        probe=type('Result',(),{'returncode':0,'stdout':'{"streams":[{"codec_type":"video"}]}'})()
        with patch.object(admin.shutil,'which',return_value='/tool'),patch.object(admin.subprocess,'run',return_value=probe):
            req=Request(self.url+'/api/upload?filename=test.mp4&preset=preview',data=b'fake video',headers={'X-Namma-Token':admin.TOKEN})
            with urlopen(req) as response:job=json.load(response)
        self.assertEqual(job['state'],'queued');self.assertEqual(job['iterations'],1000)
        self.assertEqual(Path(job['video']).read_bytes(),b'fake video')
    def test_invalid_video_leaves_no_job_or_upload(self):
        probe=type('Result',(),{'returncode':1,'stdout':''})()
        with patch.object(admin.shutil,'which',return_value='/tool'),patch.object(admin.subprocess,'run',return_value=probe):
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(self.url+'/api/upload?filename=bad.mp4',data=b'not a video',headers={'X-Namma-Token':admin.TOKEN}))
        error.exception.close()
        self.assertEqual(admin.JOBS,[]);self.assertEqual(list(self.state.glob('*.mp4')),[])

if __name__=='__main__':unittest.main()
