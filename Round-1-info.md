1. If I were judging you at IIT Bombay

I'd look at your project and ask five questions:

Judge's question	Your current approach
Can you reconstruct the place?	Yes
Does it look photorealistic?	Potentially yes
Can I freely walk through it?	Yes
Can I search "Meeting Room 4"?	Not fundamentally solved yet
Can you calculate a collision-free route around furniture/walls?	Not fundamentally solved yet
Can you repeat this reliably on a completely new IIT venue?	This is the dangerous part

And the rubric makes that very explicit.

Round 3 gives 20% each to capture, reconstruction, web UX, spatial search/path calculation, and technical Q&A.

So if you spend 90% of your effort squeezing another 5% visual quality out of NeRF/GS, you're optimizing the wrong variable.

2. The biggest mistake: treating the 3D representation as the whole solution

Your current architecture is basically:

iPhone video
     ↓
COLMAP
     ↓
Camera poses
     ↓
Gaussian Splatting
     ↓
Beautiful 3D scene
     ↓
Three.js
     ↓
WASD exploration

That is a 3D visualization pipeline.

The competition wants something closer to:

                 ┌───────────────┐
                 │ iPhone capture│
                 └───────┬───────┘
                         ↓
              Camera + Depth + Images
                         ↓
              ┌─────────────────────┐
              │ Spatial Reconstruction│
              └──────────┬──────────┘
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 Photorealistic       Geometry        Semantics
 3D representation    / occupancy       / POIs
       ↓                 ↓                 ↓
 Gaussian Splat       Floor/mesh      Room/object
       │               map              labels
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ↓
                 Spatial Engine
                         ↓
             ┌───────────┴───────────┐
             ↓                       ↓
       Search / POI             Pathfinding
             ↓                       ↓
             └───────────┬───────────┘
                         ↓
                Web / AR Navigation

That middle layer is what you're missing.

3. And there's a second problem: COLMAP is currently your weakest link

Your own project documentation says that the competition video resulted in:

2 registered images out of 810

and you responded by reducing the number of frames, lowering resolution and switching to sequential matching.

That's a reasonable emergency fix.

But as an IIT judge, I'd immediately ask:

"What happens when I give you a completely different building tomorrow?"

If your answer is:

"We need to carefully record the video, extract ~350 frames, tune COLMAP, then hope 80% register..."

that's not a robust spatial engine.

The official Round 3 specifically says you'll be assigned a completely new IIT Bombay venue, collect data according to your SOP, reconstruct it, annotate POIs and deploy the platform on-site.

That changes the engineering requirement dramatically.

4. Don't throw Gaussian Splatting away

This is important.

Your previous documentation actually had the right instinct here:

Gaussian Splatting is excellent for the visual layer.

Your setup guide describes the intended pipeline as:

iPhone video
 ↓
COLMAP
 ↓
camera poses
 ↓
Gaussian Splatting
 ↓
.splat
 ↓
Three.js

I would keep Gaussian Splatting.

But I would stop pretending that the splat itself is your navigation representation.

Think of it like this:

Gaussian Splat

Answers:

"What does this place look like?"

Spatial/occupancy representation

Answers:

"Where can I physically walk?"

Semantic layer

Answers:

"Where is the reception? Where is Meeting Room 4? Where are the sofas?"

Path planner

Answers:

"How do I get from here to there without walking through a wall?"

You need all four.

5. The method I would actually use

If I were building Namma Space for this exact competition, my architecture would be:

Capture

iPhone 15 Pro

Use:

RGB video
LiDAR depth where useful
ARKit camera poses
IMU
optionally floor-plan information if available

Your problem statement explicitly permits images, video, floor plans and sensor data.

And you already have an iPhone 15 Pro.

That is a resource you should exploit.

6. Don't make COLMAP responsible for everything

This is probably the most important technical change.

Instead of:

Video
 ↓
COLMAP must discover everything
 ↓
Camera poses

I'd aim for:

iPhone
 ├── RGB frames
 ├── ARKit poses
 ├── LiDAR depth
 └── IMU
        ↓
   pose + depth fusion
        ↓
 reliable camera trajectory

Then use COLMAP as a fallback/refinement mechanism, rather than your single point of failure.

Why?

Because you already know the failure mode.

Your current system had only 2/810 images registered.

You don't want your entire competition pipeline hanging on whether SIFT happens to find enough correspondences.

7. Your real secret weapon: build an actual spatial map

This is where I would differentiate Namma Space.

After reconstruction, generate something like:

                 TOP-DOWN MAP

       ┌───────────────────────────────┐
       │                               │
       │       ROOM A                  │
       │                               │
       │       █████████               │
       │       █           │           │
       │       █           │           │
       │───────┘           │           │
       │                   │           │
       │      CORRIDOR     │ ROOM B    │
       │                   │           │
       │                   │           │
       └───────────────────┴───────────┘

          free space = white
          obstacles = occupied

Represent this internally as an occupancy grid / navigation mesh.

For example:

0 = free
1 = obstacle
2 = wall
3 = POI

Then:

START
  ↓
A*
  ↓
collision-free path
  ↓
3D coordinates
  ↓
render path inside Gaussian Splat

Now your beautiful splat becomes the visual skin over an actual spatial engine.

That is much more defensible in a technical Q&A.

8. For pathfinding, don't run A* directly on the Gaussian Splat

This would be a classic student-project mistake.

Don't do:

Gaussian splats
      ↓
somehow detect collisions
      ↓
A*

Instead:

Depth / reconstructed geometry
             ↓
      Floor extraction
             ↓
       Occupancy map
             ↓
       obstacle inflation
             ↓
       navigation graph
             ↓
            A*
Why obstacle inflation?

Suppose your user is represented as a point.

A mathematically valid path could pass 2 cm from a chair.

A human obviously cannot.

So:

actual obstacle
      ↓
inflate by human radius
      ↓
walkable region

Then A* operates on the human-safe map.

That gives you an excellent technical answer when a judge asks:

"How do you guarantee that the path doesn't intersect furniture?"

9. POI search should be a separate intelligence layer

The problem statement isn't just asking for clickable labels.

It specifically says users should be able to search for a specific room or item and jump straight to it.

So build:

              USER
               │
       "3 seater sofas"
               ↓
        semantic search
               ↓
      ┌─────────────────┐
      │ POI database     │
      ├─────────────────┤
      │ name             │
      │ category         │
      │ position         │
      │ bounding box     │
      │ floor            │
      │ confidence       │
      └────────┬────────┘
               ↓
          destination
               ↓
             A*

Your POI database might look like:

{
  "id": "poi_024",
  "name": "Meeting Room 4",
  "category": "room",
  "position": [12.42, 0.0, -7.83],
  "floor": 1,
  "confidence": 0.94
}

Then:

"meeting room 4"
       ↓
semantic matching
       ↓
POI_024
       ↓
destination coordinates
       ↓
A*

That is much more impressive than hardcoding:

if (query === "Meeting Room 4") ...
10. You can go one step further: automatic POI discovery

This is where your AI background can actually matter.

For objects:

3D scene
 ↓
2D frames
 ↓
object detection / segmentation
 ↓
multi-view association
 ↓
3D object position
 ↓
POI

For rooms:

geometry
 +
doorways
 +
walls
 +
OCR/sign recognition
        ↓
room candidate
        ↓
"Meeting Room 4"

For example, a camera sees:

[ MEETING ROOM 4 ]

OCR extracts:

MEETING ROOM 4

You associate that with the corresponding spatial location.

Now your system can automatically create:

POI:
Meeting Room 4
x = ...
y = ...
z = ...

That directly attacks the competition's Spatial Indexing & POI Tagging criterion.

11. The biggest architectural improvement I'd make

Your current project thinks:

3D model → website

I'd change it to:

Spatial database → multiple visualizations

Something like:

                    Namma Space Engine
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ↓            ↓             ↓
         3D Gaussian    Geometry      Semantic
            Splat        / Mesh        Database
              │            │             │
              │            ↓             │
              │       Occupancy Grid     │
              │            │             │
              │            ↓             │
              │       Navigation Graph ←─┘
              │            │
              └────────────┼─────────────┐
                           ↓             ↓
                       Web Viewer     Search
                           │             │
                           └──────┬──────┘
                                  ↓
                               A* path
                                  ↓
                          3D visual route

That is an actual spatial engine.

12. Your current NeRF direction is also unnecessary

Your older pipeline documentation says:

COLMAP
 ↓
Nerfstudio
 ↓
Nerfacto
 ↓
15,000 iterations
 ↓
8–12 hours CPU

And it explicitly says your M5 Max GPU isn't currently being used, resulting in 8–12 hour training.

For this competition, I wouldn't spend time optimizing that pipeline.

You already identified the better direction in your newer setup:

COLMAP
 ↓
Splatfacto
 ↓
Gaussian Splat

Keep the splatting approach.

But move serious training to an NVIDIA GPU environment if necessary.

Your competition isn't awarding points because you trained locally on a Mac.

It cares about:

capture → reconstruction → navigation → result

13. Your SOP needs to become much more scientific

Currently your SOP is roughly:

walk slowly, good lighting, cover paths, 70–80% overlap.

Your guide specifies slow movement, good lighting, coverage, overlap and stability.

That's okay for a demo.

But an IIT judge can easily ask:

"Why 70–80%?"

"How do you know your capture has sufficient coverage?"

"How do you detect missing regions?"

"What happens if the building has a long corridor?"

You want a measurable capture protocol.

For example:

Capture SOP

Pass 1: Global trajectory

Walk the complete accessible route.

Pass 2: Geometry

Capture:

corners
doorways
intersections
stairs
large furniture
room entrances

Pass 3: POIs

Capture:

signs
room numbers
important objects

Pass 4: Quality check

Calculate:

pose continuity
frame overlap
depth coverage
tracking confidence
unmapped regions

Then tell the operator:

"Go back and capture this corridor."

That turns your system from:

video → hope

into:

capture → quality assessment → reconstruction.

14. Here's how I'd divide the actual project
Layer 1 — Capture
iPhone
├── RGB
├── LiDAR
├── ARKit pose
└── IMU

↓

Layer 2 — Reconstruction
pose estimation
      +
depth
      +
RGB
      ↓
3D geometry
      +
Gaussian Splat

↓

Layer 3 — Spatial understanding
floor
walls
doors
furniture
rooms
objects

↓

Layer 4 — Spatial database
POI
position
category
room
floor
geometry

↓

Layer 5 — Navigation
occupancy grid / navmesh
            ↓
        A* / Dijkstra
            ↓
      collision-free path

↓

Layer 6 — Web
Gaussian Splat
      +
navigation graph
      +
POIs
      +
search
      ↓
Three.js

↓

Layer 7 — AR

Only after all of that:

phone camera
     ↓
localization
     ↓
current position
     ↓
path
     ↓
AR arrows

And notice something important:

AR is bonus.

The official specification calls AR navigation a bonus worth an additional 10%.

So don't let AR eat the time needed to make the mandatory desktop navigation excellent.

15. What I'd stop doing immediately
❌ Stop obsessing over 350 vs 400 frames

That isn't the fundamental bottleneck.

❌ Stop treating 15,000 NeRF iterations as "competition quality"

Iteration count doesn't magically equal reconstruction quality.

❌ Stop using visual quality as your primary success metric

A gorgeous splat with no reliable spatial graph is still incomplete.

❌ Stop depending entirely on COLMAP

Especially after you've already experienced the 2/810 registration failure.

❌ Don't make the viewer the project

Three.js is the presentation layer.

The spatial engine is the project.

❌ Don't manually hardcode the navigation map

If you draw the path graph yourself for every location, a judge can reasonably ask:

"Where is the automation?"

16. What I would build first

If I were sitting beside you tonight, I'd prioritize it like this:

Phase 1

Get this working reliably:

iPhone
 ↓
capture
 ↓
camera poses
 ↓
Gaussian Splat
 ↓
browser

You already have most of this.

Phase 2 — MUCH MORE IMPORTANT

Build:

reconstruction
 ↓
floor geometry
 ↓
occupancy map
 ↓
A*
 ↓
visible path in Three.js

This is your biggest missing piece.

Phase 3

Add:

POI database
 ↓
search
 ↓
destination
 ↓
A*
Phase 4

Automate:

OCR
object detection
semantic labeling
Phase 5

Make capture robust:

ARKit/LiDAR
+
COLMAP fallback
+
quality metrics
Phase 6

Only then:

AR navigation
17. What your final demo should look like

Imagine the judge opens your website.

They see:

┌──────────────────────────────────────────────┐
│ NAMMA SPACE                         🔍 Search│
├──────────────────────────────────────────────┤
│                                              │
│             PHOTOREALISTIC 3D                │
│                                              │
│                  ● YOU                       │
│                   ╲                          │
│                    ╲                         │
│                     ╲━━━━━━●                │
│                            │                 │
│                     Meeting Room 4           │
│                                              │
├──────────────────────────────────────────────┤
│ Search: "3 seater sofas"                     │
│                                              │
│ Found: 3-seater sofa • Floor 1               │
│ Distance: 38 m                               │
│ [ Navigate ]                                 │
└──────────────────────────────────────────────┘

Click:

Navigate

And suddenly:

YOU ●
   │
   │
   └─────────────┐
                 │
            ┌────┘
            │
            │
            ● DESTINATION

The route visibly bends around:

██████████
   WALL
██████████

rather than passing through it.

Then the judge asks:

"How do you know this route is physically possible?"

And your answer is:

"The splat is only our visual representation. Navigation is computed independently from reconstructed geometry. We generate a walkable occupancy representation, inflate obstacles by the user clearance radius, construct the navigation graph, and run A* over that graph."

That answer sounds like an engineering system rather than a NeRF demo.

18. My assessment of your current architecture

If I were writing judge notes today:

Component	Current state	What I'd change
Smartphone capture	🟢	Add pose/depth capture
SOP	🟡	Make measurable + repeatable
COLMAP	🔴	Don't make it the sole pose source
Gaussian Splatting	🟢	Keep
NeRF/Nerfacto	🟠	Deprioritize
Web viewer	🟢	Keep improving
3D geometry	🟠	Need explicit navigable representation
POI system	🔴	Build spatial database
Search	🔴	Semantic → spatial lookup
Pathfinding	🔴	Occupancy/navmesh + A*
Collision avoidance	🔴	Explicit obstacle model
AR	🟡	Later, because bonus
On-site robustness	🔴	Highest-risk area

The official evaluation weighting makes this especially important: Spatial Search & Path Calculation is 20%, equal to reconstruction quality, web UX, capture, and the pitch/Q&A.

The architecture I'd defend to the IIT judges

If you want one sentence to anchor the whole project:

Namma Space is not a Gaussian Splat viewer. It is a spatial engine that uses Gaussian Splatting for photorealistic visualization and an independent geometric-semantic representation for POI discovery and collision-free navigation.

That's the conceptual shift I'd make right now.

Your current reconstruction work isn't wasted. The mistake would be continuing to treat reconstruction as the destination.

The actual destination is:

                 Namma Space
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
   Photorealistic          Spatial truth
   representation          representation
          │                     │
    Gaussian Splat       Geometry + POIs
          │                     │
          └──────────┬──────────┘
                     ↓
              Spatial Engine
                     │
             ┌───────┴───────┐
             ↓               ↓
           Search          A*
             │               │
             └───────┬───────┘
                     ↓
              Interactive UX
                     │
             ┌───────┴───────┐
             ↓               ↓
          Desktop            AR

That is the version I would take toward Round 2 and ultimately the IIT Bombay on-site round.