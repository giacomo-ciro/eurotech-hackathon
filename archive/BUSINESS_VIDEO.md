# Business video — 2 minutes

> Draft. Owner: Vittorio. Cross-reference: `PITCH.md`, `COMPANIES.md`, `RISK_ANALYSIS.md`. Total target = 1 min 55 s of voice-over + 5 s outro card.

## Positioning (use these words verbatim)
We are **VLA-DataEngine** — a domain-adaptation layer for lab robotics. We turn a handful of teleoperated demonstrations into auditable, domain-rich training data so small Vision-Language-Action models can speak the dialect of a specific lab. Hong Kong–first, regulated-lab–safe.

We deliberately do **not** claim to autonomously handle real patient specimens. Per `COMPANIES.md`, that framing invites regulatory pushback we can't survive in a hackathon. We talk about "specialist vocabulary in regulated, high-mix lab workflows" instead.

---

## Timing skeleton (12 beats, ~10 s each)

### [0:00 – 0:15] Hook — the real bottleneck
**Visual:** B-roll of a wet lab; cut to a researcher manually scripting a pipetting robot, then to a generalist robot arm hovering uncertainly over a rack of blood collection tubes.

> "Generalist robotics has a vocabulary problem. A small Vision-Language-Action model trained on cooking and warehouse data cannot tell a sodium-citrate vacutainer from a red-top serum tube. And the only way labs have to fix it today is to script every motion by hand, or wait months for a custom dataset."

### [0:15 – 0:30] The market we actually serve
**Visual:** Map zoom into Hong Kong; highlight HKSTP, then card stack of HKSTP biotech tenants (Insilico, Great Bay Bio, AMDL).

> "We are not selling to hospitals on day one. We are selling to the 300+ biotech R&D labs at HKSTP, the contract diagnostics labs around Kowloon Bay, and the lab-automation integrators — Automata, Opentrons, Tecan — that already ship the arms. They share one pain: every new assay forces a new robot reprogramming cycle."

### [0:30 – 0:45] The product, in one sentence
**Visual:** Whiteboard graphic of the pipeline — `few demos → ontology → Claude augmentation → verified episodes → local fine-tune → safety-gated execution → audit log`.

> "VLA-DataEngine is a data engine, not a robot. Operators record a handful of teleoperated demos on an off-the-shelf SO-101 arm. We pair those frames with a controlled lab ontology and use Claude to multiply them into hundreds of semantically rich, dialect-specific training episodes. Then a small ACT policy fine-tunes locally on a MacBook in under twenty minutes."

### [0:45 – 1:00] Why now, why us, why Hong Kong
**Visual:** Three quick stat cards.

> "Three forces converge in Hong Kong. One — HKSTP and InnoHK have built the densest lab-tech corridor in the Greater Bay Area, and they need adaptive automation. Two — Hugging Face's LeRobot stack made teleoperation cheap, but the data is still the bottleneck. Three — Claude and small VLAs like SmolVLA make it economical to keep both training and inference on-device, which is what regulated labs actually require."

### [1:00 – 1:15] Business model
**Visual:** Tiered pricing card — Dataset SKUs / Platform SaaS / Integrator partnership.

> "Three revenue lines. First, **domain dataset SKUs** — pre-augmented LeRobot datasets per vertical, sold to robotics teams who need a head start. Second, **a SaaS platform** that runs the augmentation and fine-tune loop on the customer's own demonstrations, priced per dataset generated. Third, **integrator partnerships** with lab automation vendors who white-label the engine to ship their arms task-ready."

### [1:15 – 1:30] Go-to-market — first 100 days
**Visual:** A four-step timeline.

> "First, two design-partner pilots inside HKSTP — one biotech R&D lab, one diagnostics lab — covering specimen handling and reagent prep. Second, a published before-and-after benchmark on a public SO-101 dataset so integrators can verify the lift themselves. Third, an open-source community release of the recording bridge to anchor the LeRobot developer audience. Fourth, paid pilots with one EU lab-automation vendor by month four."

### [1:30 – 1:45] The honest moat
**Visual:** Stacked diff — competitor (just synonyms) vs. us (ontology + verifier + audit log).

> "Our moat is not that Claude rewrites sentences. Anyone can do that. Our moat is the closed loop: an ontology that constrains what Claude is allowed to say, a verifier that rejects hallucinated medical terms, a safety gate between the policy and the motors, and an audit log a quality manager can sign off on. That is the difference between a demo and something a lab will plug in."

### [1:45 – 1:55] Ask + outro
**Visual:** Team photo at the SO-101 bench. Closing card.

> "We are looking for a design partner at HKSTP and an introduction to one lab-automation integrator. We are VLA-DataEngine. We make small robots speak specialist languages."

### [1:55 – 2:00] Static closing card
```
VLA-DataEngine
Adaptive data for lab robotics — built in Hong Kong
```

---

## Visual style guide
- Heavy reliance on screen captures from the running web app (Collection page during the mock recording, dataset detail with the Rerun twin replay) — keep voice-over generic enough that if a feature looks slow on the day, we can drop in B-roll without re-recording.
- Hong Kong-specific footage (skyline cutaway, HKSTP signage) anchors the geography angle. Vittorio to source.
- Pull two stat overlays from `COMPANIES.md`: "HKSTP hosts 300+ biotech companies" and "InnoHK has Health@InnoHK + AIR@InnoHK clusters."
- No medical specimens, no clinical settings on camera. Mock vacutainers only. This is intentional per `COMPANIES.md` §"strongest attack on the idea."

## Claims we will and will not make
**Will:** "auditable domain adaptation", "ontology-constrained synthetic labels", "local fine-tune on consumer hardware", "regulated-lab–aware".
**Will not:** "the robot understands medical language", "autonomously handles patient specimens", "replaces clinical staff", any FDA / CE-mark / ISO accreditation claim.

## Open items for Vittorio
- [ ] Confirm the two HKSTP design-partner targets before recording (the names mentioned at 1:15 must be real).
- [ ] Source a 5 s shot of an SO-101 arm doing the quarantine demo for the B-roll at 1:00.
- [ ] Decide whether to name a specific integrator at 1:30 (Automata is the safest public-pitch choice; concrete is better than vague).
