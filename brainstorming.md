# EuroTech x Hong Kong Hackathon Brainstorming

AI & Robotics Track  
Working document for idea selection, demo planning, and pitch asset preparation.

## Current Shortlist

| Rank | Idea | Working Name | Core Wedge | Demo Feasibility | Hong Kong Fit |
| --- | --- | --- | --- | --- | --- |
| 1 | AI robotic logistics inspection and triage | **Portbrain** | Desktop micro-sort station for high-value parcels, returns, labels, and visible risk flags | High | Very strong: HKIA cargo hub, smart logistics policy, dense high-value warehouses |
| 2 | AI-powered pharmacy dispensing assistant | **Dispenser / Dispensr** | Low-cost pharmacy workcell for packaging verification, staging, and human-in-the-loop dispensing | Medium | Strong: ageing population, bilingual healthcare workflows, dense clinics, GBA expansion |

Pitch drafts and slide/video assets should live in [`presentation_assets/`](presentation_assets/). The existing Portbrain slide deck is in [`presentation_assets/powerpoints_idea_stage/`](presentation_assets/powerpoints_idea_stage/).

## Hackathon Context

### Required Deliverables

- GitHub repository
- 2-minute business video
- 2-minute technical demo video

### Evaluation Criteria

- Originality of the idea
- Feasibility of the solution
- Potential impact
- Technical execution
- Clarity of the presentation
- Connection with the Hong Kong ecosystem

The Hong Kong connection does not require building a Hong Kong-only product. A global product can score well if Hong Kong is a credible first market, launchpad, testbed, or gateway into Asia.

### Track-Specific Resources

- AI & Robotics teams have access to SO-101 open-source robotic arms.
- Teams have access to Anthropic Claude credits.
- The strongest story should combine embodied AI, imitation learning, and a real commercial pain point rather than a generic classifier attached to a robot arm.

## Strategic Thesis

To impress a Hong Kong startup ecosystem jury, the idea should use the SO-101 arm for what it is good at: low-cost, table-top, repeatable manipulation with imitation learning and vision-language reasoning. The market story should lean into Hong Kong-specific constraints:

- High labor cost and labor shortage
- Extreme space constraints
- Dense clinics, shops, logistics sites, and service counters
- A role as a trusted gateway into the Greater Bay Area and Asia
- Strong demand for automation that fits existing workspaces rather than requiring large new facilities

The framing should be:

> We are not selling a robot arm. We are selling a low-cost automation layer for expensive, space-constrained, high-value workflows.

## Idea 1: Portbrain

### One-Line Pitch

Portbrain is a compact AI robotic inspection and triage station for Hong Kong high-value logistics operators. It classifies small parcels, detects visible issues, routes items to the right lane, and logs every decision for traceability.

### Why This Fits Hong Kong

Hong Kong logistics is shifting away from a simple "busy container port" story and toward high-value, fast, trusted, cross-border logistics.

- Hong Kong Port remains significant, but container throughput has declined compared with its historical peak; a pitch based only on container volume is weaker than it used to be.
- HKIA is the stronger anchor: Hong Kong International Airport handled **5.07 million tonnes of cargo in 2025** and was ranked the world's busiest cargo airport again.
- The Hong Kong Government's modern logistics direction explicitly emphasizes smart logistics, high-value goods, e-commerce, air/sea/land integration, and sustainable international logistics.
- Hong Kong's edge is not cheap land or mass manual labor. Its edge is trusted, space-efficient, high-value goods handling.

### Actual Workflow Reality

At the container-port level, work is mostly container movement, yard planning, customs processes, and transport coordination. The item-level work happens downstream:

1. Container or air cargo arrives.
2. Cargo is cleared, consolidated, or deconsolidated.
3. Warehouses and container freight stations handle item-level workflows.
4. Workers inspect, relabel, tag, repack, kit, sort, and prepare returns or customs documentation.

Portbrain should not claim to unload containers. It should claim to automate the value-added logistics layer after cargo has been broken down into parcels or small goods.

### Problem

Hong Kong logistics operators handle large flows of small, valuable, cross-border goods:

- Electronics
- Luxury goods
- Pharmaceuticals
- Art and collectibles
- Components and phone parts
- Returned e-commerce items
- Battery-containing devices and accessories

These items often require human workers to inspect, classify, relabel, and sort them.

Key pain points:

- **Labor pressure:** logistics work faces ageing workforce dynamics and recruiting difficulty.
- **Space pressure:** Hong Kong warehouses and freight stations are expensive and space-constrained.
- **Returns complexity:** reverse logistics requires damage checks, order verification, repacking, and manual routing.
- **Trust and traceability:** high-value goods need auditable handling decisions.

### Product

A desktop robotic station that:

1. Receives a small parcel or item in an input zone.
2. Captures image evidence from an overhead camera and optional side phone camera.
3. Classifies the item and visible handling risk.
4. Checks labels, barcodes, QR codes, hazard signs, fragile marks, damage stickers, and packaging condition.
5. Moves the item or a proxy card into an output bin.
6. Logs the decision with image, category, confidence, route, reason, and timestamp.

### Suggested Demo

**Demo title:** From mixed return bin to decisioned logistics flow.

Use 6-10 physical props:

- Small boxes
- Padded envelopes
- Fake electronics parts
- Phone case, charger, or cable
- Printed "fragile" label
- Printed "battery" label
- Printed "damaged" sticker
- QR codes or barcodes
- Red/yellow/green category cards
- Three bins: `Resell`, `Inspect`, `Hazard / Manual Review`

The arm should perform one robust pick-and-place behavior. Do not overfit the demo to arbitrary grasping.

### MVP Flow

1. Item appears in the input zone.
2. Camera captures image.
3. Vision layer produces a structured decision:
   - `standard`
   - `fragile`
   - `damaged`
   - `battery_or_electronics`
   - `manual_review`
4. Planner maps the decision to a bin.
5. SO-101 moves the item, proxy card, or label marker.
6. UI displays:
   - `Item: USB-C charger`
   - `Risk: electronics / battery handling`
   - `Decision: manual inspection`
   - `Reason: electronics item + damaged packaging`
   - `Hong Kong relevance: high-value cross-border returns`

### Technical Architecture

| Layer | Recommended Implementation | Fallback |
| --- | --- | --- |
| Perception | Claude Vision with forced JSON schema | QR/color tags and OpenCV |
| Planning | Python rules mapping class/risk to bin | Static case table |
| Robot control | LeRobot with recorded trajectories | Hard-coded waypoints |
| UI | Streamlit or Gradio dashboard | CLI plus recorded screen |
| Evidence log | CSV/JSONL event log with image paths | Screenshot table |

Example decision schema:

```json
{
  "item_name": "USB-C charger",
  "category": "electronics",
  "visible_risk": "damaged_packaging",
  "hazard_flag": true,
  "confidence": 0.87,
  "route_decision": "manual_review",
  "reason": "Electronics item with visible packaging damage should be checked before resale or onward shipping."
}
```

### Imitation Learning Plan

Do not train the robot to understand the whole world. Train it to perform a few reliable behaviors.

**Option A: Most feasible**

- Use perception to classify item.
- Use pre-recorded trajectories:
  - pick from fixed input zone
  - place in bin A
  - place in bin B
  - place in bin C
- Record 10-20 demonstrations per bin using leader-follower teleoperation.

**Option B: Stronger technical story**

- Train a conditional policy.
- Inputs:
  - camera image
  - robot state
  - instruction such as `place item in inspect bin`
- Output:
  - action chunks
- This aligns with the SmolVLA story: multi-camera views + robot state + natural language instruction condition an action expert.

**Option C: Demo fallback**

- Use fixed waypoints.
- Present imitation learning as the intended policy layer, with the waypoint controller as the hackathon reliability mode.

### Repo Structure

```text
portbrain/
  app/
    dashboard.py
    planner.py
    robot_controller.py
    vision_client.py
  prompts/
    portbrain_classifier.md
  scenarios/
    parcel_cases.csv
    sample_labels/
  motions/
    waypoints.yaml
    recorded_episodes/
  evals/
    decision_tests.csv
  assets/
    architecture.png
    demo_photos/
```

### Business Video Arc

1. Open with Hong Kong as a high-value logistics gateway.
2. Show the pain: labor-intensive inspection and routing in cramped logistics sites.
3. Introduce Portbrain as a desktop automation layer.
4. Show three rapid cases:
   - compliant parcel
   - damaged return
   - battery/electronics manual-review item
5. End with the wedge: low-cost embodied AI for space-constrained high-value logistics.

### Technical Demo Arc

1. Camera sees the item.
2. UI shows structured model output.
3. Planner selects bin.
4. Robot executes a reliable movement.
5. Event appears in the decision log.
6. Repeat with two contrasting cases.

### Risks and Guardrails

- Avoid claiming full warehouse automation.
- Avoid arbitrary grasping.
- Avoid claiming customs compliance automation unless framed as triage/support.
- Show human review for low confidence and risky items.
- Use proxies for hazardous goods.

## Idea 2: Dispenser / Dispensr

### One-Line Pitch

Dispenser is a low-cost AI pharmacy workcell that reads bilingual medicine packaging, verifies it against a prescription or instruction card, stages items into the right tray, and pauses for human confirmation when uncertain.

### Positioning Note

The raw draft uses the brand **Dispensr**. The concept can be presented as **Dispenser** while keeping **Dispensr** as the startup-style name.

### Why This Fits Hong Kong and the GBA

Hong Kong is a strong first market because:

- The population is ageing, increasing medication-management pressure.
- Clinics and retail pharmacies operate in dense, high-rent spaces.
- Medicine packaging and patient workflows are often bilingual or multilingual.
- Shenzhen and Guangzhou are close enough to support fast hardware iteration.
- A validated Hong Kong deployment is a credible bridge into the Greater Bay Area.

The GBA expansion story is especially useful: a compact, low-cost unit can start in Hong Kong clinics and then scale into a much larger regional primary-care market.

### Problem

Pharmacists spend a meaningful share of their day on repetitive operational work:

- Finding the correct medication package
- Reading labels
- Checking prescription details
- Counting, sorting, staging, or packing medicine
- Applying labels
- Resolving ambiguous packaging or instructions

The expensive systems from large pharmacy automation vendors are built for hospitals or large centralized pharmacy departments. They are often too expensive and too physically large for small clinics and community pharmacies.

### Product

A compact pharmacy dispensing assistant built on:

- SO-101 open-source robotic arm
- Computer vision for packaging and label reading
- Claude or another language model for structured parsing and disambiguation
- LeRobot imitation learning for repeated manipulation workflows
- Human-in-the-loop confirmation for uncertain or safety-sensitive cases

The safer hackathon version should stage sealed packets, blister cards, OTC boxes, or medicine proxies rather than loose pills.

### Demo Scope

Use non-prescription proxies:

- Empty blister packs
- OTC vitamin boxes
- Candy boxes as medicine stand-ins
- Printed bilingual English/Chinese labels
- Prescription or instruction cards
- Four trays: `Morning`, `Lunch`, `Dinner`, `Review`

The robot should manipulate sealed packages or cards, not loose pills.

### MVP Flow

1. Pharmacist places a package and prescription card on the mat.
2. Camera captures the package and prescription.
3. Vision/OCR extracts relevant text.
4. Reasoning layer returns:
   - `item_name`
   - `language_detected`
   - `translation`
   - `prescription_match`
   - `needs_human_confirmation`
   - `tray_assignment`
5. If confidence is high, robot moves the item to the correct tray.
6. If ambiguous, robot moves the item to `Review` and requests confirmation.

Example schema:

```json
{
  "item_name": "Vitamin D 1000 IU",
  "language_detected": ["English", "Traditional Chinese"],
  "prescription_match": true,
  "dose_timing": "morning",
  "needs_human_confirmation": false,
  "tray_assignment": "Morning",
  "reason": "Package label and instruction card both indicate morning use."
}
```

### Unit Economics Story

The business argument should be framed carefully:

- Fully loaded pharmacist time is expensive.
- A large share of counter workflow is repetitive and non-clinical.
- Incumbent automation systems are too expensive for small clinics.
- A low-cost desktop assistant can pay back faster because it targets the clinic-scale buyer.

Avoid overclaiming exact savings unless the figure is sourced in the final pitch deck. The current raw notes estimate that if 35% of a Hong Kong pharmacist's time is spent on manual dispensing, the implied annual labor value could be material; verify the salary and workflow assumptions before using those numbers on a slide.

### Technical Architecture

| Layer | Recommended Implementation | Fallback |
| --- | --- | --- |
| Perception | Camera + OCR + label crop detection | QR-coded mock labels |
| Reasoning | Claude structured parsing | Rule table from CSV |
| Safety | Human confirmation gate | Always route ambiguous cases to review |
| Robot control | LeRobot recorded motions | Fixed waypoints |
| UI | Simple pharmacist dashboard | Terminal log plus video overlay |

### Repo Structure

```text
dispensr/
  app/
    dashboard.py
    safety_gate.py
    prescription_matcher.py
    robot_controller.py
  prompts/
    label_parser.md
  sample_labels/
    english/
    chinese/
    bilingual/
  scenarios/
    prescription_cards.csv
    ambiguous_cases.csv
  motions/
    waypoints.yaml
  docs/
    safety_boundaries.md
```

### Business Video Arc

1. Open with ageing population and crowded pharmacy/clinic workflows.
2. Show a pharmacist doing repetitive packaging and tray staging.
3. Introduce Dispenser as a low-cost desktop assistant.
4. Show bilingual label reading and prescription verification.
5. Highlight the safety feature: uncertain cases pause for human confirmation.
6. End with Hong Kong as the first testbed and GBA as expansion.

### Technical Demo Arc

1. Package and instruction card enter the work area.
2. UI shows text extraction and structured interpretation.
3. Robot moves a clear case into the correct tray.
4. An ambiguous package appears.
5. System refuses to proceed autonomously and routes it to review.
6. Human confirms, then robot completes staging.

### Risks and Guardrails

- Avoid claiming autonomous clinical decision-making.
- Avoid loose-pill dispensing in the hackathon demo.
- Use sealed packaging and proxies.
- Make the human-in-the-loop safety gate visible.
- Position the product as workflow assistance, not pharmacist replacement.

## Head-to-Head Evaluation

| Criterion | Portbrain | Dispenser / Dispensr |
| --- | --- | --- |
| Originality | Medium-high: logistics sorting is known, but high-value HK micro-sort positioning is strong | Medium-high: pharmacy automation exists, but low-cost clinic workcell is compelling |
| Feasibility | Higher: parcels, labels, and bins are easy props | Medium: healthcare safety and small-object manipulation increase complexity |
| Impact | Strong: logistics scale, labor, returns, high-value goods | Strong: ageing, healthcare operations, clinic density |
| Technical execution | Clear VLM + planner + robot pipeline | Strong if label parsing and safety gate are polished |
| Presentation clarity | Very clear visual sorting demo | Clear if framed as sealed-package staging |
| Hong Kong ecosystem | Excellent fit with HKIA, GBA logistics, smart logistics policy | Strong fit with ageing, bilingual healthcare, clinic density, GBA |
| 24-hour demo reliability | Higher | Medium |
| Regulatory risk | Lower if framed as triage | Higher unless safety scope is conservative |

**Recommendation:** Portbrain is the safer first choice for a hackathon win because it gives the team a clearer, more reliable physical demo while still having a serious Hong Kong market story. Dispenser is a strong second idea if the team wants a healthcare angle, but it must be scoped around sealed packaging, staging, and human confirmation.

## 24-Hour Build Plan

### Shared Setup

- Confirm SO-101 control path.
- Confirm camera feed from phone or webcam.
- Create table layout with marked zones.
- Build a simple dashboard.
- Define JSON schemas before calling the model.
- Record demo videos as soon as the first end-to-end path works.

### Portbrain Build

1. Print labels and create parcel props.
2. Mark fixed zones: input, bin A, bin B, bin C, review.
3. Implement image capture and VLM/QR classification.
4. Implement planner rules.
5. Record or define reliable pick-and-place motions.
6. Log decisions to CSV/JSONL.
7. Record three demo scenarios.

### Dispenser Build

1. Print bilingual package labels and prescription cards.
2. Use sealed boxes/blister proxies.
3. Mark trays: morning, lunch, dinner, review.
4. Implement OCR/VLM label parsing.
5. Implement prescription match and safety gate.
6. Record or define tray placement motions.
7. Record one clear case and one ambiguous case.

## Technical Stack

- Hardware: SO-101 open-source robotic arm
- Robotics framework: Hugging Face LeRobot
- Learning approach: imitation learning from demonstrations
- VLA option: SmolVLA if setup time and compute allow
- Perception: camera feed, OpenCV, QR/barcode detection, OCR, Claude Vision
- UI: Streamlit or Gradio
- Control fallback: fixed waypoints and simple state machine

## Jury and Mentor Notes

Known AI & Robotics-relevant jury/mentor signals:

- **Grace Lai, Hong Kong Science and Technology Parks:** likely cares about pain points, market relevance, challenges, and the path from problem to solution.
- **Jayabalaji S., Intel Corporation:** avoid a demo for its own sake; show future use by real people.
- **Wendy Yau, Hong Kong-Shenzhen Innovation and Technology Park:** likely relevant to GBA launchpad framing.
- **Stepan Feduniak, InLoop Robotics:** likely relevant for robotics execution feedback.
- **Diana Munteh, angel investor / oncology background:** likely relevant for healthcare caution and pitch discipline.

Pitch implication:

- Start with the pain point, not the model.
- Show why a robot is necessary.
- Show a reliable MVP before discussing future autonomy.
- Make Hong Kong the wedge, not a decorative geography slide.

## Retired or Supporting Ideas

These ideas are useful for comparison, backup material, or future pivots.

### HarbourSeal

Desktop export-compliance triage for Hong Kong's air-cargo and GBA gateway economy. A user places a parcel and paperwork on the mat; the model reads labels, commodity hints, destination, visible hazard cues, and document completeness; the robot routes the item to clear, fix labels, or manual inspect.

Why it is useful: very strong Hong Kong cargo story, close to Portbrain, and good for adding a compliance angle.

Risk: compliance claims can become too broad. Keep it as triage, not legal clearance.

### SiteMirror

Robotic QA cell for pre-installation inspection of prefabricated construction or rail-station components. The model checks orientation, missing fasteners, label placement, and obvious spec mismatch; the robot routes parts to install or rework.

Why it is useful: strong smart-construction and infrastructure angle.

Risk: requires credible physical props and reference drawings.

### CantoDose

Multilingual medication-reconciliation and staging assistant for older adults and caregivers. It manipulates sealed packets, blister cards, or OTC boxes, translates directions, flags ambiguity, and stages items into breakfast/lunch/dinner/review trays.

Why it is useful: safer variant of Dispenser for home/care settings.

Risk: should avoid full medical autonomy and loose pills.

### TraceHand

Robotic pre-certification and authenticity triage cell for consumer goods. The robot rotates an item through camera angles while the model checks serial consistency, tamper evidence, labels, damage, and obvious brand discrepancies.

Why it is useful: good high-value goods and IP/trust story for Hong Kong.

Risk: counterfeit detection can be hard to prove without a narrow SKU library.

### ColdChain Oracle

Robotic import-food triage desk for restaurants, premium grocers, or wet-market digitization. The model checks origin labels, package integrity, timestamps, visible freshness proxies, and document consistency.

Why it is useful: distinct from generic food sorting and relevant to import-dependent Hong Kong.

Risk: avoid claiming scientific freshness detection without sensors.

### SilverAssist

Home-assistance robot for older adults, such as sorting pills or retrieving small objects.

Why it is useful: strong ageing-population angle.

Risk: small-object manipulation and home safety are difficult in a short hackathon.

### E-Waste Alchemist

AI-guided e-waste sorting for components such as batteries and PCBs.

Why it is useful: ESG and electronics supply-chain angle.

Risk: common hackathon idea; physical extraction is hard.

### Cloud-Kitchen Dim Sum Robotics

AI automation assistant for repetitive food preparation in compact Hong Kong kitchens.

Why it is useful: strong local color and labor-cost story.

Risk: dexterous food handling is mechanically risky for a short build.

## Useful Repos and References

- Hugging Face LeRobot tutorial: <https://huggingface.co/spaces/lerobot/robot-learning-tutorial>
- LeRobot real-world robot setup: <https://huggingface.co/docs/lerobot/main/en/getting_started_real_world_robot>
- SO-101 documentation: <https://huggingface.co/docs/lerobot/en/so101>
- SmolVLA documentation: <https://huggingface.co/docs/lerobot/smolvla>
- LeRobotHackathonEnv: <https://github.com/martius-lab/LeRobotHackathonEnv>
- CircuitRobot inspiration: <https://github.com/ronantakizawa/circuitrobot>
- Robotics Recyclobot inspiration: <https://github.com/TitanSage02/robotics-recyclobot>
- AMD Robotics Hackathon RadSort inspiration: <https://github.com/wilfred-dore/AMD_Robotics_Hackathon_2025_RobotROCmRadSort-main>

## Source Notes To Verify Before Final Slides

Use official or primary sources wherever possible in the final deck.

- HKIA 2025 cargo ranking and 5.07M tonnes: Airport Authority Hong Kong press release, April 2026.
- Hong Kong logistics strategy: HKSAR Government Action Plan on Modern Logistics Development.
- Hong Kong Port 2025 container throughput: Hong Kong Maritime and Port Board.
- Hong Kong ageing projections: Hong Kong Census and Statistics Department, Elderly Commission, or IMF Hong Kong reports.
- LeRobot, SO-101, and SmolVLA: Hugging Face official documentation.
- Pharmacist salary, dispensing-time percentage, and incumbent pharmacy automation pricing: still needs final source validation before using exact numbers in a pitch.
