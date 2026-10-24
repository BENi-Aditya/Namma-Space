#!/usr/bin/env python3
"""Generate honest review PDFs from current, evidence-backed project state."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT

OUT = Path(__file__).resolve().parent
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SubtitleN', fontSize=11, leading=16, textColor=colors.HexColor('#385466'), spaceAfter=16))
styles['Title'].fontName = 'Helvetica-Bold'
styles['Title'].fontSize = 25
styles['Title'].leading = 30
styles['Title'].alignment = TA_LEFT
styles['BodyText'].fontSize = 10
styles['BodyText'].leading = 14
styles['BodyText'].spaceAfter = 9
styles['Heading2'].fontSize = 13
styles['Heading2'].leading = 17
styles['Heading2'].spaceBefore = 12
styles['Heading2'].textColor = colors.HexColor('#164e63')

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#cad5dc'))
    canvas.line(42, 43, A4[0]-42, 43)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#536775'))
    canvas.drawString(42, 30, 'Namma Space | Round 1 review draft | 24 October 2026')
    canvas.drawRightString(A4[0]-42, 30, str(doc.page))

def pdf(name, pages):
    story=[]
    for index, sections in enumerate(pages):
        if index: story.append(PageBreak())
        for style, text in sections:
            story.append(Paragraph(text, styles[style]))
    SimpleDocTemplate(str(OUT/name), pagesize=A4, rightMargin=48, leftMargin=48, topMargin=44, bottomMargin=58, title=name.replace('_',' '), author='Namma Space team').build(story, onFirstPage=footer, onLaterPages=footer)

pdf('Technical_Abstract_DRAFT.pdf', [
[
('Title', 'Namma Space'),
('SubtitleN', 'Indoor reconstruction and browser exploration<br/>Technical abstract - evidence review draft<br/>Team ID: TM-C2093A5006E'),
('Heading2', '1. Problem and Round 1 scope'),
('BodyText', 'Namma Space turns ordinary smartphone captures of an accessible indoor space into reconstructed 3D assets for remote browser exploration. The Round 1 focus is a repeatable capture procedure, reliable reconstruction and a zero-install walkthrough. POI labeling and obstacle-aware desktop routing are deferred to Round 2; AR navigation is a later bonus.'),
('Heading2', '2. Architecture'),
('BodyText', '<b>Capture video &rarr; frame sampling &rarr; COLMAP camera estimation &rarr; learned reconstruction &rarr; PLY export &rarr; manifest &rarr; Three.js browser viewer.</b> The supported pipeline keeps original captures, processed data and trained checkpoints outside the app source. Every new run receives a unique ID and never deletes an existing run.'),
('BodyText', 'Two output paths are distinguished. The existing Gaussian asset was trained externally and is rendered by GaussianSplats3D. A locally tested Mac route uses Nerfacto with PyTorch MPS and exports a colored point cloud. A NeRF point cloud is not a Gaussian export and does not have the visual behavior of a neural renderer.'),
('Heading2', '3. Present evidence and boundaries'),
('BodyText', 'The local viewer loads the existing 650,682-vertex Gaussian PLY and preserved NeRF mesh/cloud assets. A 10-step Mac MPS compatibility test saved a checkpoint using 20 resized frames and existing camera poses. This is not an end-to-end reproduction or a model-quality result. The Gaussian overview is fragmented; room fidelity and a useful indoor starting view remain acceptance work.'),
('BodyText', '<b>Review draft:</b> final deployment URL, source capture/configuration for IMG_2008, contributor attribution, full reconstruction evidence and the demonstration video are not yet complete. This abstract must be updated after those checks; it is not a submission-ready claim.')
],
[
('Title', 'Capture and reconstruction'),
('Heading2', '4. Capture SOP'),
('BodyText', 'Choose a permission-cleared room with stable lighting, clear walkable access and visible texture. Walk slowly along an overlapping loop, keeping nearby furniture, corners and the floor-to-wall boundary in view. Add transitions between different room views rather than filming disconnected panoramas. Avoid motion blur, rapid turns, mirrors, blank walls and moving people where practical.'),
('BodyText', 'The project capture guide recommends high-resolution phone video and overlapping eye-level, lower and higher passes. These are proposed capture settings, not a claim about every existing clip. The included older local sample is 36.7 seconds at 1280 x 720 and 30 fps. Record actual capture settings, room coverage and input hashes for the chosen final run.'),
('Heading2', '5. Pose estimation and quality gates'),
('BodyText', 'The supported runner asks Nerfstudio to sample approximately 300 frames and perform sequential COLMAP matching. Before training, it checks at least 20 registered frames, finite 4 x 4 camera matrices and valid RGB references. The minimum frame count is an engineering safeguard, not an official competition threshold or a guarantee of successful reconstruction.'),
('BodyText', 'Existing processed datasets contain 252 and 306 posed frames respectively, with referenced RGB files present. This shows usable preprocessing artifacts exist, but not that they cover the complete room correctly. Inspect pose continuity, missing areas and input/output correspondence before spending time on a longer training run.'),
('Heading2', '6. Training and exports'),
('BodyText', 'The installed environment includes Nerfstudio 1.1.5, PyTorch 2.3.1 and gsplat 1.4.0. A Mac MPS tensor allocation and a small torch Nerfacto run succeeded. The installed Gaussian rasterization stack uses CUDA and has not been validated for Metal training. The local fallback therefore uses torch Nerfacto without mixed precision; quality and memory must be measured before choosing a larger run.'),
('BodyText', 'Exports are checked before manifest registration. Gaussian PLY files are distinguished from ordinary XYZ/color point clouds. Original datasets/checkpoints stay in place, and the run records preserve commands, requested iterations and failure state. A fresh complete video-to-viewer run remains unverified.')
],
[
('Title', 'Browser system and validation'),
('Heading2', '7. Interactive viewer'),
('BodyText', 'A static Three.js application loads a model manifest, renders Gaussian splats or fallback mesh/point-cloud assets and provides WASD camera movement. Enter walkthrough requests first-person mouse look, with Escape to release it. An embedded browser may block pointer lock; a hold-and-drag look fallback is provided. Reset recovers the overview, while an optional editor preserves the existing alignment and asset controls.'),
('BodyText', 'Loading is serialized to avoid concurrent model replacements. Missing manifest and loading failures are surfaced to the user. Controls clear movement on focus/visibility changes. Reconstruction units are explicitly uncalibrated: model dimensions must not be represented as metres without a measured scale reference. Collision prevention and route planning are not implemented for this round.'),
('Heading2', '8. Portability and reproduction'),
('BodyText', 'The supported app now lives inside apps/viewer rather than an absolute symlink to another local folder. The localhost launcher serves only the app directory and does not stop another process to claim its port. A packaging script copies the runtime, notices, manifest and referenced artifacts into a standalone static directory, resolving local symlinks for deployment.'),
('BodyText', 'The source repository does not carry the large Gaussian export through ordinary Git. A fresh clone requires a documented artifact distribution and a reviewed sample capture in the test directory. The actual older source clip is copied locally under test/data with a SHA-256 record, but public sharing of its audio and interior content needs owner review.'),
('Heading2', '9. Verification and limitations'),
('BodyText', 'Regression tests cover existing-run preservation, missing images, non-finite poses and manifest integrity after failed export. Source checks validate local asset references, runtime imports and syntax. These checks do not prove high fidelity, a fresh installation, public availability or sustained browser performance.'),
('BodyText', 'The final acceptance run must show recognizable indoor structure, sustained keyboard/mouse roaming, sensible start/reset behavior, and signed-out access to the deployed URL. Measure load time and frame behavior with a named device/browser. No FPS, accuracy, full-training runtime or competition score is claimed here.')
],
[
('Title', 'Reproducibility and credits'),
('Heading2', '10. Submission evidence to finalize'),
('BodyText', 'The supplied competition brief specifies 31 October 2026 for Round 1, without a cutoff hour/timezone. The final Drive folder must contain this abstract (at most five pages), an organized viewer/repository link document, a 3-5 minute capture-and-walkthrough demonstration and code/setup with sample data inside a test directory. Confirm portal changes and permissions before submission.'),
('BodyText', 'Repository: <link href="https://github.com/BENi-Aditya/Namma-Space" color="#164e63">github.com/BENi-Aditya/Namma-Space</link>. Public viewer URL: not yet supplied/deployed. The organized links document records this as missing rather than using a fictitious URL.'),
('Heading2', '11. Third-party foundations'),
('BodyText', 'Rendering builds on Three.js r167 and GaussianSplats3D 0.4.7 (MIT). Their licence texts accompany the vendored runtime. Reconstruction builds on Nerfstudio 1.1.5 and gsplat 1.4.0 (Apache-2.0), PyTorch (BSD-style), COLMAP (BSD), and FFmpeg (licence depends on build). Historical mesh export uses Open3D (MIT). Retain applicable notices and review upstream distribution terms before redistributing binaries.'),
('BodyText', 'The existing IMG_2008 export was described in prior project metadata as trained with a friend. Its exact source capture, training settings/checkpoint, contributor identity and permission to redistribute must be confirmed. This draft does not claim that this external model was independently reproduced during the audit.'),
('Heading2', '12. Technical conclusion'),
('BodyText', 'The reusable foundation is a local reconstruction workspace, real captured inputs, existing trained artifacts and a portable web viewer. The immediate technical priority is a traceable, recognizable single-room reconstruction and an accepted desktop walkthrough. Public deployment, final video and complete reproduction evidence are mandatory remaining gates. Optional spatial search/navigation work must not displace them.'),
('BodyText', '<b>Evidence files:</b> docs/audit/2026-10-24; docs/REPRODUCTION.md; test/assets.json; apps/viewer/THIRD_PARTY_NOTICES.md. Revise this draft when the final run, URLs and contributor details are available.')
]
])
pdf('Additional_Links_and_Prototypes_DRAFT.pdf', [[
('Title', 'Links and prototypes'),
('SubtitleN', 'Namma Space | Team TM-C2093A5006E<br/>Organized master document - incomplete review draft'),
('Heading2', 'Code repository'),
('BodyText', '<link href="https://github.com/BENi-Aditya/Namma-Space" color="#164e63">https://github.com/BENi-Aditya/Namma-Space</link><br/>Use the final published revision referenced in the verification record. Setup: README.md and docs/REPRODUCTION.md. Reviewed source sample must accompany the submitted test/data directory.'),
('Heading2', 'Proof of concept and web viewer'),
('BodyText', '<b>MISSING: publicly accessible HTTPS viewer URL.</b><br/>The current localhost preview is not an acceptable remote demo link. Deploy output/site, test it while signed out on a second device, then replace this section with the actual working URL. Demonstrate WASD and mouse free roaming without installing software.'),
('Heading2', 'Demonstration video'),
('BodyText', '<b>MISSING: final 3-5 minute demonstration.</b><br/>The storyboard is prepared, but no final narrated video is claimed. Include the actual capture process and an indoor web walkthrough. Place the final video inside the Round 1 Drive folder; add a link here only if using an additional video host.'),
('Heading2', 'Model and sample distribution'),
('BodyText', 'Large local artifacts are not included through ordinary Git. Provide a reviewed model archive and sample capture, clear ownership/contributor rights, and preserve the paths and hashes in test/assets.json. Current sample audio/interior sharing has not been reviewed for public release.'),
('Heading2', 'Final access checks'),
('BodyText', 'Replace missing sections before submission. Put the completed abstract, this master document, the video and code/sample materials in one organized Google Drive folder. Set view access to anyone with the link, verify signed-out access, and submit the folder URL through the Techfest portal. No final submission or permission check has been performed.')
]])
print('Created 4-page abstract draft and 1-page organized links draft.')
