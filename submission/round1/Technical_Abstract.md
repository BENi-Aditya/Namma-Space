# Terra Space - Technical Abstract

Team ID: TM-C2093A5006E

# Terra Space

## Spaces, made explorable.

A practical pipeline from smartphone capture to interactive 3D viewing.

Team ID: TM-C2093A5006E


## From captured space<br/>to shared exploration.

A local reconstruction workflow connected to an interactive, publicly accessible 3D model library.

Terra Space integrates smartphone capture, camera-pose estimation, learned reconstruction and browser visualization. Its contribution is workflow integration, not a new reconstruction algorithm.

Architecture: capture and reconstruction -> model presentation -> versioned web publication.


### Local training studio

A browser-based interface accepts video uploads and coordinates processing, training and export. Persistent job history, live logs, cancellation and measured training progress make the workflow inspectable.


### Public spatial viewer

A static web application loads scenes from a manifest. Visitors explore with orbit and keyboard controls, enter first-person viewing, or use Edit mode to inspect alignment and crop settings.


## Good reconstruction starts<br/>before training.

A repeatable capture procedure and explicit validation gates connect raw video to usable scene assets.


### 01  PLAN

Choose a permitted indoor space. Keep lighting stable and reduce moving objects. Plan connected views around furniture and room boundaries.


### 02  CAPTURE

Move slowly with overlapping views. Include corners, floor-to-wall boundaries and changes in height. Avoid blur, fast turns and reflective surfaces.


### 03  REVIEW

Check sharpness, continuity and coverage. Retain the source recording and its capture settings. Associate inputs and outputs with a unique run ID.


### Frame extraction

Sample video into images suitable for feature matching.


### Camera estimation

COLMAP estimates poses from overlapping image features.


### Pre-training checks

Require registered frames, finite camera matrices and valid image references.


### Training and export

Run the selected reconstruction route; check outputs before library registration.

Jobs run sequentially with visible failure states. Training ETA is measured from step progress; preprocessing and export do not have assumed completion times.


## Different representations.<br/>One exploration interface.

The viewer supports Gaussian, mesh and point-cloud assets without treating their visual or geometric properties as interchangeable.


### Reconstruction routes

Gaussian training uses CUDA in the installed Splatfacto/gsplat stack. The Mac route uses Nerfacto with MPS and exports a colored point cloud. Mesh and point-cloud assets use Three.js; Gaussian assets use GaussianSplats3D.


### Explore the scene

Orbit, WASD and vertical movement support free exploration. First-person mode requests mouse capture; Escape releases it. Drag-based looking provides a fallback where pointer lock is unavailable.


### Inspect and refine

Edit mode exposes rotation, translation, scale, clipping and display controls. For example, a user can level a floor, crop peripheral artifacts or choose a useful initial viewing direction.

Alignment and cropping do not recover missing surfaces. Units are uncalibrated; collision prevention is not implemented.


## A consistent view,<br/>as the library grows.

Saved scene state and verified assets make the published experience reproducible across model additions and revisions.

Save Position & Lock records scene settings in the manifest. Commit and push trigger asset snapshotting and Vercel publication with SHA-256 verification and versioned asset URLs.


### Published defaults

The committed scene configuration initializes each visit. New exports can join the library without redesigning the viewer.


### Visitor experimentation

Public Edit mode changes the current visit only. Reopening restores the published configuration; owner saves remain local.


### Validation strategy and scope

Input checks, failed-export safeguards, manifest validation and saved-state tests protect the workflow. Browser review checks loading, navigation and editing. Reconstruction fidelity, coverage and performance require separate scene-specific evaluation; no universal accuracy, FPS or training-time guarantee is asserted. POI search, obstacle-aware routing and AR are outside the implemented scope.

Credits: Nerfstudio, gsplat, PyTorch, COLMAP, FFmpeg, Three.js, GaussianSplats3D and Open3D. Retain licences and asset-contributor attribution.


Public viewer: https://terraspace.openbuilder.in/

Code and setup: https://github.com/BENi-Aditya/Namma-Space
