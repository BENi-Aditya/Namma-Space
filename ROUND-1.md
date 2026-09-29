Namma Space — Master Execution Plan & AI Agent Operating Document

Project: Namma Space
Competition: IIT Bombay Techfest 2026–27
Current priority: Complete and submit Round 1: 3D Reconstruction & Roaming
Document purpose: This is the master execution contract for the AI coding/research agent and the human team.

0. READ THIS FIRST

Namma Space must not be treated as only a "3D model viewer".

The competition asks for an end-to-end intelligent spatial engine that turns ordinary indoor captures into a photorealistic, interactive 3D environment, supports free browser roaming, and eventually adds POI search and collision-free indoor navigation.

The official Round 1 focus is narrower:

SOP construction

3D model reconstruction

Free-roaming web viewer

Clear technical documentation

Demonstration video

Reproducible code/sample data

Round 2 adds POIs and desktop pathfinding. Round 3 requires the complete system to work on a new venue captured on-site at IIT Bombay.

Therefore:

We will build the architecture for the complete Namma Space system, but we will only implement what is necessary and reliable for Round 1 before the Round 1 submission deadline.

The official problem statement explicitly requires a reliable 3D model, zero-install browser walkthrough, and an SOP for capture. Round 1 evaluates SOP/pipeline soundness, visual quality/model fidelity, web viewer performance, and documentation/video clarity.

1. THE CORE STRATEGIC CHANGE

What we have today

The current project is approximately:

iPhone video
    ↓
FFmpeg frames
    ↓
COLMAP
    ↓
camera poses + sparse point cloud
    ↓
Nerfstudio / NeRF or Gaussian Splatting
    ↓
3D model
    ↓
Three.js / React viewer

This is a reasonable 3D reconstruction + visualization pipeline.

It is not yet a complete spatial engine.

What Namma Space should become

The target architecture is:

                    NAMMA SPACE
                         │
          ┌──────────────┴──────────────┐
          │                             │
   VISUAL REPRESENTATION         SPATIAL TRUTH
          │                             │
   Gaussian Splatting            Geometry / Depth
          │                      Occupancy / Navmesh
          │                      Semantic Objects
          │                      POIs / Metadata
          │                             │
          └──────────────┬──────────────┘
                         │
                  SPATIAL ENGINE
                         │
             ┌───────────┴───────────┐
             │                       │
          SEARCH                  NAVIGATION
             │                       │
          POI → XYZ              A* / Navmesh
                                     │
                              obstacle-aware path
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                    DESKTOP WEB                AR
                    WALKTHROUGH              BONUS

The most important architectural principle is:

Gaussian Splatting is the visual layer. It must not be the only representation of spatial truth.

A splat is excellent for photorealistic visualization. Navigation requires explicit information about floors, walls, obstacles, free space and connectivity.

2. COMPETITION REQUIREMENTS

Round 1

Official focus

SOP
 ↓
3D reconstruction
 ↓
free-roaming browser viewer

Required submission

The Round 1 submission folder must contain:

Technical Abstract PDF

maximum 5 pages

system architecture

pipeline design

SOP construction

technical approach

Proof of Concept / Web Viewer document

working web-viewer link

free-roaming demonstration

Demonstration video

3–5 minutes

project scope

capture process

3D web walkthrough

Code repository

setup instructions

reconstruction instructions

sample data inside a test directory

Round 1 evaluation areas

SOP & Pipeline Soundness
Visual Quality & Model Fidelity
Web Viewer Performance
Documentation & Video Clarity

Round 1 does NOT require us to fully implement POI search, navigation, or AR.

Those must be architecturally planned, but they should not consume Round 1 implementation time at the expense of reconstruction reliability.

3. PROJECT OBJECTIVES

Primary objective

Build a reliable pipeline that takes an ordinary smartphone capture of an indoor environment and produces:

capture
  ↓
camera / spatial information
  ↓
3D reconstruction
  ↓
photorealistic representation
  ↓
web-ready model
  ↓
interactive browser walkthrough

Secondary objective

Design the internal representation so that Round 2 can add:

3D scene
   ↓
POIs
   ↓
spatial search
   ↓
walkable representation
   ↓
A* / navigation

Final objective

By Round 3:

new IIT Bombay venue
        ↓
SOP-guided capture
        ↓
automated processing
        ↓
3D digital twin
        ↓
POI extraction / annotation
        ↓
desktop search
        ↓
collision-free navigation
        ↓
optional AR navigation

4. PHASE ROADMAP

Phase 0 — Project Audit & Architecture Freeze

Goal

Understand the current repository and stop architectural drift.

Tasks

Inspect the entire current repository.

Identify current scripts and entry points.

Identify current reconstruction pipeline.

Identify current web viewer.

Identify which parts are working.

Identify which parts are experimental.

Identify duplicate or conflicting pipelines.

Document all assumptions.

Freeze the architecture for Round 1.

Create the new experimental spatial-engine folder.

Preserve the existing viewer layout/design where useful.

Deliverables

docs/
  ARCHITECTURE.md
  CURRENT_STATE.md
  DECISIONS.md

experiments/
  spatial-engine-v2/

Acceptance criteria

Anyone on the team can understand the current pipeline.

There is exactly one documented Round 1 primary pipeline.

Experimental approaches are separated from the stable pipeline.

No existing working implementation is destroyed.

Status

Not started

In progress

Complete

5. PHASE 1 — CAPTURE SOP

Goal

Create a repeatable Standard Operating Procedure that another person can follow.

The SOP is a competition deliverable, not just an internal note.

Capture strategy

The SOP should define:

Environment preparation

Turn on available lights.

Avoid rapidly changing illumination.

Remove unnecessary moving objects if possible.

Keep doors in a consistent state.

Avoid people moving through the capture area.

Ensure the route is physically accessible.

Camera

Primary capture device:

iPhone

The exact capture settings should be recorded rather than assumed.

The SOP must document:

resolution

frame rate

lens/camera used

stabilization setting

orientation

exposure considerations

whether LiDAR/depth is available

whether ARKit pose data is available

Movement

The operator should:

move slowly

avoid sudden rotations

avoid fast panning

maintain continuous coverage

capture corners

capture doorways

capture intersections

capture important visual landmarks

avoid large jumps in viewpoint

Coverage

The operator should not simply walk in a straight line.

The route should deliberately cover:

room entrance
→ room perimeter
→ important corners
→ furniture
→ doors
→ corridors
→ intersections
→ return / loop closure

Overlap

The existing project guidance recommends substantial frame overlap and slow movement.

The actual SOP should eventually express this as measurable capture requirements rather than vague instructions.

SOP quality checks

Before processing, verify:

Entire target area captured

No major unexplored region

Corners captured

Doorways captured

Important objects visible

Camera movement stable

Lighting acceptable

No long periods of motion blur

Capture route provides loop closure where possible

Original video preserved

Phase 1 deliverables

docs/
  SOP.md
  SOP_CHECKLIST.md

data/
  captures/
    <scene-name>/
      original/
      metadata/

Acceptance test

A second team member should be able to read the SOP and capture a new room without verbal guidance.

Status

Not started

In progress

Complete

6. PHASE 2 — RELIABLE CAMERA / POSE PIPELINE

Goal

Make camera pose estimation reliable enough that reconstruction does not depend on a brittle single tool.

Current problem

The existing project experienced a severe COLMAP failure where only a very small number of frames were successfully registered.

This means:

COLMAP must not be treated as an unquestionable single point of failure.

New strategy

Use a layered approach:

Primary:
iPhone spatial information / ARKit / depth / motion data
             ↓
Strong camera pose prior

Secondary:
COLMAP / SfM
             ↓
visual refinement / fallback / reconstruction support

The exact combination must be experimentally validated.

Do not implement a complex fusion system just because it sounds good.

First prove each available signal independently.

Experiments

Experiment A — COLMAP only

Measure:

number of frames

registered frames

percentage registered

reconstruction scale

camera trajectory

failure locations

Experiment B — phone pose data

Measure:

pose continuity

drift

coverage

availability

exportability

Experiment C — depth / LiDAR

Measure:

depth coverage

missing depth regions

noise

usable geometry

alignment with RGB

Experiment D — combined pipeline

Only after A/B/C are understood:

phone pose
+
depth
+
visual features

Test whether the combination improves robustness.

Required metrics

Every reconstruction experiment must record:

input frames
registered frames
registration %
processing time
model size
training time
viewer load time
visual quality notes
failure regions

Do not write:

"This looks better."

Instead write:

"Experiment B registered 92% of frames compared with 31% in Experiment A."

Phase 2 acceptance criteria

A capture should produce a usable camera trajectory without manual camera placement.

The pipeline should also clearly report failure instead of silently generating a bad model.

Status

Not started

In progress

Complete

7. PHASE 3 — RECONSTRUCTION REPRESENTATION BENCHMARK

Goal

Select the reconstruction representation based on actual results.

Candidate methods:

COLMAP + NeRF
COLMAP + Gaussian Splatting
Phone pose/depth + Gaussian Splatting
Hybrid reconstruction

The current documentation contains both NeRF/Nerfstudio and Splatfacto/Gaussian Splatting references. These should not remain as two undocumented "official" pipelines.

We need one declared Round 1 primary pipeline.

Benchmark criteria

Each method should be evaluated on:

Metric

Meaning

Registration reliability

Can the scene be reconstructed?

Visual fidelity

Does the model resemble reality?

Geometry stability

Are surfaces spatially consistent?

Training time

Can the team iterate quickly?

Model size

Can the web app load it?

Viewer performance

Is roaming smooth?

Failure rate

How often does it break?

Reproducibility

Can another machine reproduce it?

Important principle

Do not choose a method because:

it is newer

it sounds more AI

it is popular

it produced one impressive screenshot

Choose based on:

reliability × visual quality × reproducibility × web performance

Round 1 recommendation

The working architectural direction is:

Gaussian Splatting
+
explicit spatial metadata

because photorealistic browser visualization is a central requirement.

However, the agent must benchmark the actual environment before declaring it final.

Phase 3 acceptance criteria

A representative indoor capture must:

reconstruct successfully,

preserve recognizable room geometry,

preserve important visual details,

export to a web-friendly representation,

load in the browser,

support free movement.

Status

Not started

In progress

Complete

8. PHASE 4 — WEB VIEWER

Goal

Deliver a clean, zero-install browser experience for Round 1.

Important rule

The new spatial-engine architecture should use a similar viewer layout to the existing Namma Space web viewer.

Do not redesign the entire frontend unnecessarily.

Preserve useful existing components:

viewer
camera controls
loading screen
scene container
basic UI shell

Then build the spatial-engine version separately.

9. NEW EXPERIMENTAL FOLDER

Create a new folder so the new architecture does not destabilize the existing working viewer.

Recommended:

experiments/
└── spatial-engine-v2/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── STATUS.md
    │
    ├── capture/
    │   ├── README.md
    │   └── experiments/
    │
    ├── reconstruction/
    │   ├── README.md
    │   ├── pipelines/
    │   └── experiments/
    │
    ├── spatial/
    │   ├── README.md
    │   ├── geometry/
    │   ├── occupancy/
    │   ├── navmesh/
    │   └── semantics/
    │
    ├── viewer/
    │   ├── README.md
    │   ├── src/
    │   ├── public/
    │   └── package.json
    │
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── test/
    │
    ├── scripts/
    │   ├── capture/
    │   ├── reconstruction/
    │   ├── conversion/
    │   └── validation/
    │
    └── docs/
        ├── experiments/
        ├── decisions/
        └── benchmarks/

This folder is the next-generation spatial engine.

It should be developed without deleting the current stable implementation.

10. VIEWER REQUIREMENTS

Round 1 minimum

The viewer must provide:

web browser access

no installation for the judge

scene loading

first-person camera

WASD movement

mouse look

collision behaviour if feasible

loading state

useful error state

reasonable performance

Viewer UI

Recommended layout:

┌─────────────────────────────────────────────┐
│ NAMMA SPACE                     STATUS ●    │
├─────────────────────────────────────────────┤
│                                             │
│                                             │
│              3D VIEWER                     │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│ WASD Move     Mouse Look     ESC Controls   │
└─────────────────────────────────────────────┘

Do not overload the Round 1 viewer with navigation features that are not ready.

11. PHASE 5 — ROUND 1 QUALITY & VALIDATION

Goal

Turn "it works on my laptop" into a measurable submission.

Create an automated/manual validation checklist.

Reconstruction validation

[ ] Capture exists
[ ] Capture follows SOP
[ ] Frame extraction succeeds
[ ] Camera estimation succeeds
[ ] Reconstruction completes
[ ] Model export succeeds
[ ] Model file is web-compatible
[ ] Browser loads model
[ ] Camera starts in valid location
[ ] Movement works
[ ] Major room geometry is recognizable
[ ] No catastrophic holes/artifacts

Browser validation

Test:

Chrome
Safari
Edge

At minimum document the tested browser(s).

Measure:

initial load time

model size

memory use if practical

frame-rate feel

movement smoothness

camera clipping

black-screen failures

network loading failures

12. PHASE 6 — ROUND 1 DOCUMENTATION

Goal

Produce professional documentation before the final week.

Required documents:

docs/
├── README.md
├── SOP.md
├── ARCHITECTURE.md
├── PIPELINE.md
├── SETUP.md
├── REPRODUCTION.md
├── TROUBLESHOOTING.md
├── BENCHMARKS.md
├── EXPERIMENT_LOG.md
└── ROUND1_SUBMISSION.md

13. TECHNICAL ABSTRACT PLAN

Maximum 5 pages.

Recommended structure:

Page 1 — Problem & Solution

Problem

Namma Space

objective

system overview

Page 2 — Capture SOP

smartphone capture

movement protocol

coverage

overlap

quality checks

Page 3 — Reconstruction Pipeline

capture
→ preprocessing
→ pose estimation
→ reconstruction
→ export

Include architecture diagram.

Page 4 — Web Viewer

browser architecture

3D representation

controls

performance

Page 5 — Results

input capture

reconstructed model

viewer screenshots

metrics

limitations

future roadmap

14. DEMONSTRATION VIDEO PLAN

Target:

3–5 minutes

Recommended structure:

0:00–0:20

Problem statement.

0:20–0:50

Show physical room.

0:50–1:20

Show capture SOP.

1:20–2:00

Show processing pipeline.

2:00–3:30

Show web viewer.

3:30–4:20

Show technical architecture.

4:20–5:00

Show result and future spatial-navigation architecture.

Do not spend the majority of the video on terminal commands.

The judge should see:

REAL SPACE
   ↓
CAPTURE
   ↓
RECONSTRUCTION
   ↓
WEB DIGITAL TWIN
   ↓
FREE ROAMING

15. ROUND 1 SUBMISSION STRUCTURE

Create a final submission directory:

round1-submission/
│
├── 01-technical-abstract/
│   └── Namma-Space-Technical-Abstract.pdf
│
├── 02-web-viewer/
│   └── Web-Viewer-Link.md
│
├── 03-demo-video/
│   └── Demo-Link.md
│
├── 04-code/
│   └── Repository-Link.md
│
├── 05-documentation/
│   ├── SOP.md
│   ├── ARCHITECTURE.md
│   ├── PIPELINE.md
│   └── REPRODUCTION.md
│
└── 06-evidence/
    ├── screenshots/
    ├── capture/
    └── reconstruction/

Before submission:

[ ] Google Drive access = anyone with link can view
[ ] Technical Abstract ≤ 5 pages
[ ] Web viewer link works
[ ] Demo video = 3–5 min
[ ] Repository is accessible
[ ] Sample data exists in test directory
[ ] Setup instructions tested
[ ] All links tested from an incognito browser

16. POST-ROUND-1 ROADMAP

After Round 1 submission, stop optimizing only the visual layer.

The project becomes a true spatial engine.

PHASE 7 — EXPLICIT GEOMETRY

Goal

Extract a representation of the physical space that is independent of the photorealistic renderer.

Target:

RGB / depth / reconstruction
          ↓
      geometry
          ↓
 floor + walls + obstacles

Possible representations:

point cloud
mesh
depth map
voxel grid
occupancy grid

The implementation should be selected experimentally.

PHASE 8 — WALKABLE SPACE

Goal

Create a computational representation of where a person can walk.

Example:

floor
████████████████████████
█                      █
█   FREE SPACE         █
█                      █
█       █████          █
█       █TABLE         █
█       █████          █
█                      █
████████████████████████

Convert this into:

walkable = 1
obstacle = 0

or an equivalent navigation mesh.

PHASE 9 — OBSTACLE INFLATION

A path that mathematically touches a wall is not a useful human walking path.

Therefore:

physical obstacle
       ↓
inflate by user radius + safety margin
       ↓
navigation obstacle

Example:

Actual table:

    █████
    █████

Navigation representation:

   █████████
   █████████

This gives the path planner clearance.

PHASE 10 — PATHFINDING

Goal

Implement actual indoor navigation.

Pipeline:

POI destination
      ↓
destination XYZ
      ↓
nearest walkable node
      ↓
navigation graph
      ↓
A*
      ↓
collision-free path
      ↓
3D coordinates
      ↓
render path in viewer

The path planner must not run directly on Gaussian splats.

PHASE 11 — POI SYSTEM

POI schema

Every POI should have something similar to:

{
  "id": "meeting-room-a",
  "name": "Meeting Room A",
  "category": "room",
  "position": [x, y, z],
  "floor": 0,
  "confidence": 0.97,
  "source": "manual"
}

Possible categories:

room
door
desk
chair
reception
washroom
stair
elevator
equipment
object

PHASE 12 — SEMANTIC EXTRACTION

Possible pipeline:

images
  ↓
OCR / object detection / segmentation
  ↓
2D detections
  ↓
multi-view association
  ↓
3D position
  ↓
POI database

Potential capabilities:

room-number OCR

sign recognition

object detection

object categories

semantic regions

manual correction

Important:

Automated semantic extraction should assist the system, not make the entire competition demo depend on imperfect AI predictions.

PHASE 13 — SEARCH

User:

"Meeting Room 4"

System:

text query
   ↓
POI search
   ↓
matching POI
   ↓
3D destination
   ↓
route

Search should support:

exact name

partial name

category

synonyms

object type

PHASE 14 — DESKTOP NAVIGATION UX

Target interaction:

Search
"Meeting Room 4"

        ↓

Meeting Room 4
[Go there]

        ↓

route calculated

        ↓

3D path appears

        ↓

user follows path

The path should be rendered as a visible 3D line, arrows, or equivalent visual guide.

PHASE 15 — ROUND 2 INTEGRATION

Round 2 target:

3D digital twin
+
POI system
+
search
+
walkable map
+
A*
+
desktop navigation

Round 2 deliverables include:

updated repository

live web app

3–5 minute demo

POI/search/navigation demonstration

PHASE 16 — ROUND 3 FIELD ROBUSTNESS

Goal

Make the system work on an unfamiliar IIT Bombay venue.

This is where the architecture is truly tested.

The system must be able to go from:

unknown venue
       ↓
SOP
       ↓
capture
       ↓
processing
       ↓
reconstruction
       ↓
POIs
       ↓
navigation
       ↓
deployment

PHASE 17 — CAPTURE QUALITY AUTOMATION

Before processing everything, automatically report:

coverage
pose continuity
blur
exposure
frame overlap
tracking confidence
depth coverage
unmapped regions

Then:

PASS
or
RECAPTURE REQUIRED

This is much more scalable than relying on human intuition.

PHASE 18 — AR NAVIGATION

AR is explicitly a bonus.

Therefore:

Do not allow AR development to delay the mandatory desktop navigation pipeline.

Target:

camera
 ↓
localization
 ↓
current user position
 ↓
destination
 ↓
route
 ↓
AR arrows / guidance

Only begin once:

reconstruction
+
POIs
+
desktop navigation

are stable.

19. MASTER ARCHITECTURE

The final Namma Space architecture should evolve toward:

                    ┌─────────────────────┐
                    │     SMARTPHONE      │
                    │ RGB / VIDEO / DEPTH │
                    │ POSE / IMU / LiDAR  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   CAPTURE PIPELINE  │
                    │       + SOP         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  POSE / RECON       │
                    │ COLMAP / ARKit etc. │
                    └──────────┬──────────┘
                               │
               ┌───────────────┴────────────────┐
               ▼                                ▼
     ┌────────────────────┐          ┌────────────────────┐
     │ VISUAL REPRESENT.  │          │ SPATIAL REPRESENT. │
     │ Gaussian Splatting │          │ Geometry / Depth   │
     │                    │          │ Occupancy / Mesh   │
     └──────────┬─────────┘          └──────────┬─────────┘
                │                               │
                │                               ▼
                │                    ┌────────────────────┐
                │                    │ SEMANTIC LAYER     │
                │                    │ POIs / Objects     │
                │                    └──────────┬─────────┘
                │                               │
                │                               ▼
                │                    ┌────────────────────┐
                │                    │ SPATIAL DATABASE   │
                │                    └──────────┬─────────┘
                │                               │
                │                   ┌───────────┴──────────┐
                │                   ▼                      ▼
                │             ┌────────────┐        ┌────────────┐
                │             │   SEARCH   │        │ NAVIGATION │
                │             └─────┬──────┘        │ A* / Mesh  │
                │                   │               └─────┬──────┘
                │                   └──────────┬──────────┘
                │                              ▼
                └──────────────────────► ┌───────────────┐
                                         │ WEB VIEWER    │
                                         │ Three.js      │
                                         │ First Person  │
                                         └───────┬───────┘
                                                 │
                                     ┌───────────┴──────────┐
                                     ▼                      ▼
                                DESKTOP WEB                AR

20. REPOSITORY STRUCTURE

Recommended long-term repository:

namma-space/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── apps/
│   ├── web-viewer/
│   └── spatial-viewer/
│
├── pipeline/
│   ├── capture/
│   ├── preprocessing/
│   ├── pose/
│   ├── reconstruction/
│   ├── export/
│   ├── geometry/
│   ├── semantics/
│   └── navigation/
│
├── experiments/
│   └── spatial-engine-v2/
│
├── data/
│   ├── test/
│   ├── examples/
│   └── generated/
│
├── scripts/
│
├── docs/
│   ├── SOP.md
│   ├── ARCHITECTURE.md
│   ├── PIPELINE.md
│   ├── BENCHMARKS.md
│   ├── TROUBLESHOOTING.md
│   ├── EXPERIMENT_LOG.md
│   └── decisions/
│
├── round1/
├── round2/
└── round3/

21. AI AGENT OPERATING INSTRUCTIONS

The AI coding/research agent must follow these rules.

Rule 1 — Work phase by phase

Never attempt to implement the entire final system at once.

Always work in this order:

Phase 0
↓
Phase 1
↓
Phase 2
↓
Phase 3
↓
Phase 4
↓
Phase 5
↓
Phase 6
↓
Round 1 submission
↓
Phase 7+

Rule 2 — Do not skip acceptance criteria

A phase is not complete because code exists.

A phase is complete only when:

implementation
+
test
+
documentation
+
evidence

exist.

Rule 3 — Do not destroy the working pipeline

The existing viewer and reconstruction pipeline may be imperfect.

Do not replace it blindly.

Instead:

existing/
   ↓
stable baseline

experiments/spatial-engine-v2/
   ↓
new architecture

Promote a new implementation into the main pipeline only after validation.

Rule 4 — Every experiment gets logged

For every experiment record:

Experiment ID
Date
Goal
Input
Method
Parameters
Hardware
Software versions
Runtime
Output
Metrics
Failure modes
Conclusion
Next action

Rule 5 — Never use vague conclusions

Bad:

"Gaussian Splatting worked better."

Good:

"Pipeline B produced a complete reconstruction in 38 minutes, registered 94% of input frames, generated a 312 MB web model, and loaded successfully in Chrome."

Rule 6 — Prefer measurable engineering decisions

Whenever two approaches are possible:

A vs B

create a benchmark.

Do not make architectural decisions based only on intuition.

Rule 7 — Separate visual truth from spatial truth

Always maintain this distinction:

Visual representation:
"what does the scene look like?"

Spatial representation:
"where can a person physically move?"

The first can be Gaussian Splatting.

The second should use geometry/depth/occupancy/navmesh or another explicit spatial representation.

Rule 8 — Do not build navigation directly on splats

Gaussian Splatting is a rendering representation.

Navigation requires:

floor
walls
obstacles
free space
connectivity

Build those explicitly.

Rule 9 — Round 1 comes first

If a task does not improve Round 1:

SOP
reconstruction
web viewer
documentation
demo
reproducibility

it should normally be deferred.

Especially defer:

AR
complex semantic AI
advanced search
large backend systems
unnecessary UI redesign

unless they are needed for an architecture experiment.

Rule 10 — Keep the human team informed

After each phase, report:

Completed:
...

Evidence:
...

Metrics:
...

Problems:
...

Decision:
...

Next phase:
...

22. PHASE STATUS SYSTEM

Use these statuses:

⬜ NOT STARTED
🟡 IN PROGRESS
🔵 BLOCKED
🟢 COMPLETE
🔴 FAILED / NEEDS REDESIGN

A phase marked COMPLETE must have evidence.

23. MASTER PROGRESS TRACKER

Phase

Objective

Priority

Status

0

Audit & architecture freeze

P0

⬜

1

Capture SOP

P0

⬜

2

Reliable pose pipeline

P0

⬜

3

Reconstruction benchmark

P0

⬜

4

Web viewer

P0

⬜

5

Quality validation

P0

⬜

6

Round 1 documentation/submission

P0

⬜

7

Explicit geometry

P1

⬜

8

Walkable space

P1

⬜

9

Obstacle inflation

P1

⬜

10

A* / navigation

P1

⬜

11

POI system

P1

⬜

12

Semantic extraction

P1

⬜

13

Search

P1

⬜

14

Desktop navigation UX

P1

⬜

15

Round 2 integration

P1

⬜

16

Round 3 field robustness

P2

⬜

17

Capture quality automation

P2

⬜

18

AR navigation

P3

⬜

24. ROUND 1 GATE

We do not move to Round 2 work until this checklist is green.

Capture

SOP finalized

SOP tested by another person

Competition capture completed

Original data preserved

Reconstruction

Pipeline reproducible

Pose estimation succeeds

Reconstruction succeeds

Model quality acceptable

Model exported successfully

Viewer

Public/accessible URL

Loads without local installation

First-person movement works

Mouse look works

Scene is recognizable

No critical runtime errors

Documentation

Technical Abstract complete

SOP documented

Architecture documented

Setup instructions tested

Reproduction instructions tested

Benchmarks documented

Video

3–5 minutes

Physical capture shown

Pipeline explained

Web viewer shown

Final result clearly demonstrated

Submission

Drive folder prepared

Access tested from incognito

All links verified

Repository accessible

Sample data included

Only after all of this:

ROUND 1 = COMPLETE

25. DECISION LOG

Every major architectural decision must be recorded.

Template:

# Decision: <TITLE>

Date:
Phase:

## Problem

What were we deciding?

## Options

### Option A
...

### Option B
...

## Evidence

...

## Decision

...

## Reason

...

## Revisit Condition

We will reconsider this if:
...

Example:

# Decision: Reconstruction Representation

Date: YYYY-MM-DD
Phase: 3

## Options

- Nerfacto
- Splatfacto
- Other tested method

## Evidence

See BENCHMARKS.md

## Decision

...

## Revisit Condition

If browser performance or reconstruction reliability falls below the
required threshold, benchmark the next candidate.

26. EXPERIMENT LOG

Use:

docs/EXPERIMENT_LOG.md

Template:

# EXP-001

Date:
Phase:
Owner:

## Question

What are we trying to learn?

## Input

Dataset:
Frames:
Resolution:
Capture duration:

## Method

...

## Configuration

...

## Results

Registered frames:
Registration %:
Runtime:
Model size:
Viewer load time:

## Observations

...

## Conclusion

...

## Decision

...

## Next Experiment

...

27. BENCHMARK DASHBOARD

Maintain a single table:

Experiment

Pipeline

Frames

Registered

Runtime

Model Size

Viewer

Result

EXP-001

COLMAP + X

-

-

-

-

-

-

EXP-002

Pose + X

-

-

-

-

-

-

EXP-003

Hybrid

-

-

-

-

-

-

The agent must update this after every meaningful reconstruction experiment.

28. DEFINITION OF DONE

A feature is DONE only when:

[1] Implemented
[2] Tested
[3] Measured where applicable
[4] Documented
[5] Reproducible
[6] Integrated

A research idea is DONE only when:

[1] Hypothesis stated
[2] Experiment performed
[3] Results recorded
[4] Conclusion recorded
[5] Decision made

29. WHAT NOT TO DO

Do not:

endlessly tune frame count without measuring the actual bottleneck

blindly increase training iterations

assume COLMAP is always reliable

call a beautiful render a successful spatial reconstruction

build navigation directly over splats

hardcode a navigation map that cannot generalize

add AR before mandatory desktop navigation

redesign the UI every time the backend changes

delete the stable viewer while experimenting

keep multiple undocumented "official" pipelines

hide failed experiments

claim success without evidence

spend Round 1 time polishing Round 2 features

30. IMMEDIATE EXECUTION ORDER

NOW

Step 1

Create:

experiments/spatial-engine-v2/

Step 2

Create:

README.md
ARCHITECTURE.md
STATUS.md
docs/

Step 3

Audit the current project.

Document:

what works
what fails
what is experimental
what is stable

Step 4

Run a controlled reconstruction benchmark.

At minimum compare:

current pipeline
vs
new pose/depth-assisted pipeline if available

Step 5

Do not optimize the final architecture until the benchmark has evidence.

Step 6

Freeze the Round 1 pipeline.

Step 7

Build the production-quality Round 1 viewer.

Step 8

Validate everything.

Step 9

Prepare the Round 1 submission package.

Step 10

Only after Round 1 is safely complete, begin:

geometry
→ occupancy
→ navigation
→ POIs
→ search
→ Round 2

31. AI AGENT FIRST TASK

When this document is given to the AI agent, its first response/action should be:

1. Inspect the repository.
2. Inspect the current reconstruction pipeline.
3. Inspect the current web viewer.
4. Inspect all existing documentation.
5. Create experiments/spatial-engine-v2/.
6. Create the project status and architecture documents.
7. Produce a Phase 0 audit.
8. Do NOT begin implementing later phases yet.
9. Report the Phase 0 findings.
10. Propose the smallest set of experiments needed to begin Phase 1/2.

The agent must not immediately rewrite the entire project.

32. FINAL ENGINEERING PRINCIPLE

Namma Space should evolve from:

"video → pretty 3D model"

into:

"real space → machine-readable spatial model → photorealistic digital twin
→ searchable semantic environment → walkable spatial graph → navigation"

The photorealistic model is what the user sees.

The spatial representation is what the computer understands.

The web application is where both meet.

That separation is the foundation of the complete Namma Space system.

33. SOURCE-OF-TRUTH NOTE

This document is based on the current Namma Space project documentation and the official Techfest problem statement.

The official competition material defines Round 1 around SOP, 3D reconstruction, free-roaming, and the specified submission artifacts. Round 2 introduces POI labeling and desktop pathfinding, while Round 3 tests the complete system on a new IIT Bombay venue.

The existing project documentation contains multiple reconstruction references, including COLMAP + NeRF and COLMAP + Splatfacto/Gaussian Splatting. This master plan therefore treats the reconstruction method as an engineering decision to be benchmarked rather than assuming the existing documentation is already a finalized architecture.

34. CURRENT MASTER STATUS

NAMMA SPACE
────────────────────────────────────────────

ROUND 1
├── Phase 0  Audit / Architecture       ⬜
├── Phase 1  Capture SOP                ⬜
├── Phase 2  Pose / Reconstruction      ⬜
├── Phase 3  Representation Benchmark   ⬜
├── Phase 4  Web Viewer                 ⬜
├── Phase 5  Validation                 ⬜
└── Phase 6  Submission                 ⬜

ROUND 2
├── Phase 7  Geometry                   ⬜
├── Phase 8  Walkable Space             ⬜
├── Phase 9  Obstacle Inflation         ⬜
├── Phase 10 A* Navigation              ⬜
├── Phase 11 POIs                       ⬜
├── Phase 12 Semantic Extraction        ⬜
├── Phase 13 Search                     ⬜
├── Phase 14 Navigation UX              ⬜
└── Phase 15 Round 2 Integration        ⬜

ROUND 3
├── Phase 16 Field Robustness           ⬜
├── Phase 17 Capture QA Automation      ⬜
└── Phase 18 AR Navigation              ⬜

────────────────────────────────────────────

CURRENT MISSION:

        █████████████████████████████
        █  COMPLETE ROUND 1 FIRST  █
        █████████████████████████████

Do not optimize the entire future system before
we have a reliable Round 1 submission.