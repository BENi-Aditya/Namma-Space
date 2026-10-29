"""Build the visual technical abstract and its editable text companion."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'output/pdf/Terra_Space_Technical_Abstract_Draft.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=595.28,841.89
INK='#2F2822'; TEAL='#9A5738'; MUTED='#76695E'; LINE='#E4D6C7'; PALE='#F7EFE5'; GOLD='#C49A54'; PAPER='#FCF8F2'
pdfmetrics.registerFont(TTFont('TerraSerif','/System/Library/Fonts/Supplemental/Georgia.ttf'))
pdfmetrics.registerFont(TTFont('TerraBold','/System/Library/Fonts/Supplemental/Georgia Bold.ttf'))
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('Terra Space | Technical Abstract');c.setAuthor('Terra Space team')
source=['# Terra Space - Technical Abstract','Team ID: TM-C2093A5006E']
def rect(x,y,w,h,fill,stroke=None):
    c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor(stroke or fill));c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
def text(x,y,s,size=10,color=INK,bold=False):
    c.setFillColor(colors.HexColor(color));c.setFont('TerraBold' if bold else 'Helvetica',size);c.drawString(x,H-y-size,s)
def para(x,y,w,s,size=10.5,color=INK,maxh=200):
    p=Paragraph(s,ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=size*1.43,textColor=colors.HexColor(color),alignment=TA_LEFT))
    _,h=p.wrap(w,maxh)
    assert h<=maxh,(s[:60],h,maxh)
    p.drawOn(c,x,H-y-h)
    return h

def page(n,kicker,title,subtitle):
    rect(0,0,W,H,PAPER);rect(0,0,9,H,TEAL)
    text(38,26,'TERRA SPACE',10,TEAL,True);text(330,26,'TECHFEST, IIT BOMBAY  |  ROUND 1',8,MUTED)
    text(38,77,kicker.upper(),9,TEAL,True)
    para(38,99,520,title,28,INK,85)
    para(38,173,510,subtitle,11,MUTED,55)
    rect(38,788,519,1,LINE)
    text(38,803,'TECHNICAL ABSTRACT  /  TEAM TM-C2093A5006E',8,MUTED)
    text(516,800,f'{n:02d} / 05',9,TEAL,True)
    source.extend(['\n## '+title,subtitle])
def section(x,y,w,title,body):
    text(x,y,title,12,TEAL,True);para(x,y+25,w,body,maxh=160)
    source.extend(['\n### '+title,body])
def card(x,y,w,h,label,body):
    rect(x,y,w,h,PALE);rect(x,y,3,h,TEAL)
    text(x+15,y+15,label,11,INK,True);para(x+15,y+39,w-30,body,10,maxh=h-49)
    source.extend(['\n### '+label,body])
def arrow(x1,y1,x2,y2):
    c.setStrokeColor(colors.HexColor(TEAL));c.setLineWidth(1.5);c.line(x1,H-y1,x2,H-y2)
    p=c.beginPath();p.moveTo(x2,H-y2);p.lineTo(x2-5,H-y2+3);p.lineTo(x2-5,H-y2-3);p.close();c.setFillColor(colors.HexColor(TEAL));c.drawPath(p,fill=1,stroke=0)
def finish(): c.showPage()
def cover():
    rect(0,0,W,H,'#F2E7D8');rect(0,0,W,15,TEAL)
    text(45,48,'TERRA SPACE',12,TEAL,True)
    text(45,94,'TECHNICAL ABSTRACT',9,MUTED,True)
    c.setFont('TerraSerif',38);c.setFillColor(colors.HexColor(INK));c.drawString(45,H-163,'Spaces, made')
    c.drawString(45,H-207,'explorable.')
    para(47,227,420,'A practical pipeline from smartphone capture to interactive 3D viewing.',15,MUTED,55)
    rect(45,315,505,300,'#2F2822')
    img=ROOT/'submission/round1/viewer-scene-screenshot.png'
    if img.exists():
        c.saveState();c.setFillColor(colors.white);c.roundRect(58,H-600,479,250,8,fill=1,stroke=0);c.clipPath(c.beginPath()) if False else None
        c.drawImage(ImageReader(str(img)),58,H-600,width=479,height=250,preserveAspectRatio=True,anchor='c',mask='auto');c.restoreState()
    else:
        for i,(label,value) in enumerate([('CAPTURE','phone video'),('RECONSTRUCT','local pipeline'),('EXPLORE','web viewer')]):
            x=70+i*160;text(x,405,label,9,'#EBD8BE',True);text(x,440,value,12,'#FFFFFF')
    para(45,654,470,'A local-first system for preparing, reconstructing, editing and sharing indoor spaces.',12,INK,70)
    rect(45,748,505,1,GOLD);text(45,765,'TEAM TM-C2093A5006E',9,TEAL,True);text(345,765,'TECHFEST  /  ROUND 1',9,MUTED,True)
    source.extend(['# Terra Space','## Spaces, made explorable.','A practical pipeline from smartphone capture to interactive 3D viewing.','Team ID: TM-C2093A5006E'])
    c.showPage()

cover()
page(2,'01 / Concept & system architecture','From captured space<br/>to shared exploration.','A local reconstruction workflow connected to an interactive, publicly accessible 3D model library.')
para(38,241,519,'Terra Space integrates smartphone capture, camera-pose estimation, learned reconstruction and browser visualization. It brings video preparation, local training, scene editing and web publication into one practical workflow.',11,maxh=100)
source.append('Terra Space integrates smartphone capture, camera-pose estimation, learned reconstruction and browser visualization. Its contribution is workflow integration, not a new reconstruction algorithm.')
text(38,355,'ONE WORKFLOW, THREE RESPONSIBILITIES',9,TEAL,True)
for x,label,body in [(38,'RECONSTRUCT','Video + camera poses<br/>Training + exports'),(218,'PRESENT','Model library<br/>Navigation + editing'),(398,'PUBLISH','Versioned assets<br/>Shared web experience')]:
    rect(x,383,159,100,INK);text(x+13,400,label,11,'#FFFFFF',True);para(x+13,427,135,body,10,'#EBD8BE',48)
arrow(197,433,215,433);arrow(377,433,395,433)
source.append('Architecture: capture and reconstruction -> model presentation -> versioned web publication.')
section(38,521,245,'Local training studio','A browser-based interface accepts video uploads and coordinates processing, training and export. Persistent job history, live logs, cancellation and measured training progress make the workflow inspectable.')
section(312,521,245,'Public spatial viewer','A static web application loads scenes from a manifest. Visitors explore with orbit and keyboard controls, enter first-person viewing, or use Edit mode to inspect alignment and crop settings.')
rect(38,704,519,56,PALE)
para(53,716,489,'<b>Design principle:</b> keep expensive reconstruction local, then distribute portable scene assets and explicit presentation settings through the web.',10.5,maxh=40)
finish()

page(3,'02 / Capture SOP & orchestration','Good reconstruction starts<br/>before training.','A repeatable capture procedure and explicit validation gates connect raw video to usable scene assets.')
card(38,239,164,154,'01  PLAN','Choose a permitted indoor space. Keep lighting stable and reduce moving objects. Plan connected views around furniture and room boundaries.')
card(216,239,164,154,'02  CAPTURE','Move slowly with overlapping views. Include corners, floor-to-wall boundaries and changes in height. Avoid blur, fast turns and reflective surfaces.')
card(394,239,163,154,'03  REVIEW','Check sharpness, continuity and coverage. Retain the source recording and its capture settings. Associate inputs and outputs with a unique run ID.')
text(38,425,'PROCESSING AND QUALITY GATES',9,TEAL,True)
stages=[('Frame extraction','Sample video into images suitable for feature matching.'),('Camera estimation','COLMAP estimates poses from overlapping image features.'),('Pre-training checks','Require registered frames, finite camera matrices and valid image references.'),('Training and export','Run the selected reconstruction route; check outputs before library registration.')]
for i,(label,body) in enumerate(stages):
    y=455+i*62
    rect(38,y,29,29,TEAL);text(47,y+7,str(i+1),11,'#FFFFFF',True)
    text(82,y,label,11,INK,True);para(82,y+19,465,body,10,MUTED,35)
    source.extend(['\n### '+label,body])
rect(38,716,519,48,PALE)
para(52,726,491,'<b>Operational reliability:</b> jobs run sequentially; failures remain visible. Training ETA uses observed step progress, while preprocessing and export have no assumed completion time.',10,maxh=35)
source.append('Jobs run sequentially with visible failure states. Training ETA is measured from step progress; preprocessing and export do not have assumed completion times.')
finish()

page(4,'03 / Reconstruction & interaction','Different representations.<br/>One exploration interface.','The viewer supports Gaussian, mesh and point-cloud assets without treating their visual or geometric properties as interchangeable.')
rows=[('Representation','Technical route','Rendering implications'),('Gaussian splats','Splatfacto / gsplat training;\nCUDA in the installed stack.','Gaussian primitives rendered\nwith GaussianSplats3D.'),('NeRF-derived point cloud','Nerfacto on Mac MPS;\nexport sampled colored points.','A sampled representation,\nnot a full neural renderer.'),('Mesh / point-cloud assets','Compatible exported geometry\nregistered in the manifest.','Three.js geometry rendering;\ncontrols depend on asset type.')]
widths=[135,191,193]
for ri,row in enumerate(rows):
    y=240+ri*62;x=38
    for col,(s,w) in enumerate(zip(row,widths)):
        rect(x,y,w,62,INK if ri==0 else (PALE if ri%2 else '#FFFFFF'),LINE if ri else None)
        para(x+11,y+14,w-22,s.replace('\n','<br/>'),9.3,'#FFFFFF' if ri==0 else INK,45);x+=w
source.extend(['\n### Reconstruction routes','Gaussian training uses CUDA in the installed Splatfacto/gsplat stack. The Mac route uses Nerfacto with MPS and exports a colored point cloud. Mesh and point-cloud assets use Three.js; Gaussian assets use GaussianSplats3D.'])
section(38,520,245,'Explore the scene','Orbit, WASD and vertical movement support free exploration. First-person mode requests mouse capture; Escape releases it. Drag-based looking provides a fallback where pointer lock is unavailable.')
section(312,520,245,'Inspect and refine','Edit mode exposes rotation, translation, scale, clipping and display controls. For example, a user can level a floor, crop peripheral artifacts or choose a useful initial viewing direction.')
rect(38,704,519,60,PALE)
para(53,715,489,'<b>Geometric limits:</b> alignment and cropping change presentation; they do not recover missing surfaces. Scene units are uncalibrated, and free movement does not currently prevent collisions.',10.5,maxh=43)
source.append('Alignment and cropping do not recover missing surfaces. Units are uncalibrated; collision prevention is not implemented.')
finish()

page(5,'04 / Publication, validation & foundations','A consistent view,<br/>as the library grows.','Saved scene state and verified assets make the published experience reproducible across model additions and revisions.')
text(38,239,'LOCAL EDITS',10,TEAL,True);text(218,239,'COMMIT + PUSH',10,TEAL,True);text(398,239,'PUBLIC RELEASE',10,TEAL,True)
arrow(135,247,207,247);arrow(325,247,387,247)
para(38,271,519,'Save Position &amp; Lock records the camera, transform, crop and display settings in the model manifest. The publishing hook snapshots referenced exports into compressed, versioned parts. Deployment restores the assets, checks SHA-256 integrity and packages the static viewer for Vercel. Content-versioned URLs help browsers retrieve changed assets.',10.5,maxh=90)
source.append('Save Position & Lock records scene settings in the manifest. Commit and push trigger asset snapshotting and Vercel publication with SHA-256 verification and versioned asset URLs.')
card(38,370,250,102,'Published defaults','The committed scene configuration initializes each visit. New exports can join the library without redesigning the viewer.')
card(307,370,250,102,'Visitor experimentation','Public Edit mode changes the current visit only. Reopening restores the published configuration; owner saves remain local.')
section(38,494,519,'Validation strategy and scope','Input checks, failed-export safeguards, manifest validation and saved-state tests protect the workflow. Browser review checks loading, navigation and editing. Reconstruction fidelity, coverage and performance require separate scene-specific evaluation; no universal accuracy, FPS or training-time guarantee is asserted. POI search, obstacle-aware routing and AR are outside the implemented scope.')
text(38,620,'OPEN-SOURCE FOUNDATIONS',9,TEAL,True)
para(38,642,519,'Reconstruction builds on Nerfstudio and gsplat (Apache-2.0), PyTorch and COLMAP (BSD-style), and FFmpeg (build-dependent licence). Rendering uses Three.js and GaussianSplats3D (MIT); historical mesh export uses Open3D (MIT). Applicable notices and asset-contributor attribution must accompany distributed materials. The project contributes integration and workflow design rather than new reconstruction algorithms.',9.4,MUTED,78)
source.append('Credits: Nerfstudio, gsplat, PyTorch, COLMAP, FFmpeg, Three.js, GaussianSplats3D and Open3D. Retain licences and asset-contributor attribution.')
para(38,733,519,'<b>Explore:</b> <link href="https://terraspace.openbuilder.in/" color="#9A5738">terraspace.openbuilder.in</link><br/><b>Code &amp; setup:</b> <link href="https://github.com/BENi-Aditya/Namma-Space" color="#9A5738">github.com/BENi-Aditya/Namma-Space</link>',10,maxh=35)
source.extend(['\nPublic viewer: https://terraspace.openbuilder.in/','Code and setup: https://github.com/BENi-Aditya/Namma-Space'])
finish();c.save()
(ROOT/'submission/round1/Technical_Abstract.md').write_text('\n\n'.join(source)+'\n')
print(OUT)
