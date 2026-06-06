# Ideas

## In the Right Direction

### Expired Scout
**Key idea:** Robot scans a shelf with a camera, reads expiry dates, and physically pulls out expired items — replacing the most tedious compliance task in retail.

**HK angle:** Tiny overstocked convenience stores (7-Eleven, Watsons) face real compliance liability from missed expired goods.

**Feedback:** n/a

### The Drink Whisperer

**Key idea:** Camera identifies a half-finished drink; robot picks the correct bottle and tops it up autonomously — simple object recognition + learned pouring motion.

**HK angle:** High F&B labor costs and tiny bar footprints make partial drink-service automation immediately credible.

**Feedback:** n/a

### Pill Witness

**Key idea:** Robot watches an elderly person's hand via camera, identifies the correct pill from a weekly organizer, and only releases it after visually confirming the person has swallowed — turning medication adherence from a passive reminder into a physically enforced ritual.

**HK angle:** HK's rapidly aging population has seniors living alone in subdivided flats with chronic medication non-adherence costing the healthcare system billions annually.

**Feedback:** Interesting.

### Stamp Clerk

**Key idea:** Robot reads a handwritten address 
label with its camera, picks the correct postage stamp from a sorted tray, and precisely affixes it — replacing the most error-prone step in small-business daily shipping.

**HK angle:** Solo cross-border e-commerce sellers in cramped flats hand-label dozens of packages daily with no room or budget for a label printer.

**Feedback:** Interesting.

### Crack Prober

**Key idea:** Robot drags a stylus along a wall surface at constant speed, using motor torque fluctuations to detect and map micro-cracks invisible to camera — AI overlays defect trace onto a visual map.

**HK angle:** HK's aging public housing estates require mandatory structural inspections that are expensive and dangerously manual on high-rise façades.

**Feedback:** Interesting, but not immediate to scale.

### Seal Stamper

**Key idea:** Robot reads a document with its camera, identifies the designated stamp box, picks the correct company chop from a rack, and applies it with calibrated pressure at pixel-perfect alignment.

**HK angle:** HK and GBA businesses process enormous volumes of physical contracts requiring official company seals, with misplaced stamps causing costly legal delays.

**Feedback:** Interesting.

### Label Inspector
**Key idea:** Robot picks a medication bottle, Claude Vision reads the label — if occluded or glare-obscured, arm rotates incrementally until fully legible, then reads dosage info aloud. The bottle physically cooperates with the camera until vision succeeds.
**HK angle:** Elderly HK residents living alone misread medication labels daily; a bedside device that orients the bottle until it can read it removes the last barrier between label and patient.
**Feedback:** Interesting.

### Doubt Resolver
**Key idea:** Conveyor carries mixed recyclables past a camera; Claude Vision classifies each item and flags low-confidence detections — the arm physically flips, rotates, or lifts the object to expose a new angle, re-runs the classifier, and iterates until confidence crosses the threshold before sorting.
**HK angle:** HK's MSW levy creates commercial pressure for high-accuracy automated sorting in dense building clusters sharing centralized recycling points.
**Feedback:** Good idea.

### Stage Shadow
**Key idea:** Arm holds a directional mic and tracks a moving speaker via Claude Vision — if audio quality drops (clipping, reverb, voice drop-off), the arm repositions to re-aim the mic using sound itself as the error signal to physically correct capture geometry.
**HK angle:** HK's one-person live-commerce and streaming economy runs in micro-studios where a fixed mic produces dead audio the moment the host moves and a sound engineer is unaffordable.
**Feedback:** Interesting.

## Wrong Direction

### Saucer Setter
**Key idea:** Claude Vision reads a meal ticket, identifies the dish, and robot picks the correct condiment cups from a rack and places them on the tray — replacing repetitive mis-plating in high-volume dim sum service.
**HK angle:** Dim sum restaurants turn over hundreds of trays per hour; condiment mis-sets are the #1 table complaint and too fiddly for fixed automation.
**Feedback:** Useless.

### Cable Whisperer
**Key idea:** Robot traces cables by color/label via camera then physically lifts, reroutes, and clips each one into a labeled channel — autonomous cable management.
**HK angle:** HK's dense co-working spaces and server-room-in-a-closet setups create chronic cable chaos IT support charges a premium to fix.
**Feedback:** Overkill, not a real problem.

### Queue Jumper
**Key idea:** Robot watches ticket dispenser and counter display via camera; when gap drops below threshold, physically presses "next" to pace queue flow — no software integration required.
**HK angle:** HK government offices and clinics run legacy ticket queue systems that chronically bunch; plug-and-play physical regulator fits zero-IT-access institutions.
**Feedback:** Overkill, arm is not needed.

### Blind Packer
**Key idea:** Robot uses motor torque feedback while pressing down after each placement to build a real-time resistance map of a box interior, letting Claude decide optimal next-item position — packing tighter than vision-only systems.
**HK angle:** HK e-commerce micro-fulfillment in sub-100 sqft units where denser packing directly cuts courier fees.
**Feedback:** Overkill.

### Signature Witness
**Key idea:** Robot watches a live signature via camera, compares it stroke-by-stroke against a stored reference, and physically stamps "VERIFIED" or "REJECTED" on the document.
**HK angle:** HK's legal/financial sector processes millions of wet signatures for cross-border GBA contracts where forgery verification is still done by eye.
**Feedback:** Not useful.

### Posture Ghost
**Key idea:** Claude Vision detects poor posture onset and the robot physically nudges a prop to trigger a correction — unavoidable physical intervention instead of a screen notification.
**HK angle:** HK's subdivided flat workers and long-hour desk culture drive high rates of chronic neck/back pain with no space for ergonomic furniture.
**Feedback:** Not enough value added, overkill.

### Card Sharp
**Key idea:** Robot watches a business card exchange via camera, reads the card's text with Claude Vision, and files it physically into the correct labeled slot of a desktop organizer.
**HK angle:** HK's hyper-networked business culture generates enormous card volumes at trade fairs; cards still end up unsorted in drawers.
**Feedback:** Not enough value added.

### Ripeness Oracle
**Key idea:** Robot presses fruit with calibrated force, reads resistance curve via motor torque to classify firmness, and separates stock into sell-today vs. sell-tomorrow piles.
**HK angle:** HK wet market vendors lose 15–20% of perishable stock to misjudged sell-timing in cramped stalls with no refrigerated staging.
**Feedback:** Needs lots of labeled calibration data — not feasible in 24h.



### Mirror Calligrapher

**Key idea:** Robot watches a human write Chinese characters live and mirrors the stroke sequence with a brush — live imitation learning, not pre-programmed templates.

**HK angle:** Calligraphy is culturally resonant in HK/GBA.

**Feedback:** Too hard to implement in 24h.

### Blind Spot Surgeon

**Key idea:** Robot uses motor current feedback as haptic sense to re-seat PCB connectors in occluded spaces where vision fails — AI interprets resistance spikes as a real-time touch map.

**HK angle:** Replaces rare, expensive "fix by feel" skill in Sham Shui Po electronics repair shops.

**Feedback:** Too complex, requires well-calibrated sensors.

### Plant Doctor

**Key idea:** Robot probes soil at grid points using motor resistance as a moisture/compaction map, then waters only dry zones with surgical precision.

**HK angle:** Rooftop farms and indoor micro-gardens in HK's vertical buildings.

**Feedback:** Discarded.

### Knot Teacher

**Key idea:** Robot demonstrates knot-tying step-by-step, watches the child attempt via camera, and repeats only the sub-step where hands deviated — closed-loop physical tutoring.

**HK angle:** Overstretched childcare system leaves fine-motor skill gaps in children in high-density flats.

**Feedback:** Knots are extremely difficult; dexterity is still an open research problem. Not feasible.

### Lock Auditor

**Key idea:** Robot tests every drawer and cabinet by physically attempting to open each one, using motor resistance as binary lock/open detection — giving security teams an audit trail no camera can produce.

**HK angle:** Dense co-working spaces across Kowloon and Central handle thousands of daily users with shared storage.

**Feedback:** Useless.

### Sushi Counter

**Key idea:** Robot watches a chef portion fish via camera, detects off-standard slice thickness, and physically repositions the guide rail before the next cut — AI physically corrects the next action.

**HK angle:** Premium Japanese restaurants pay top wages for skilled chefs during a chronic GBA chef shortage.

**Feedback:** Not interested.

### Tremor Anchor

**Key idea:** Robot watches an elderly person's hand via camera, detects tremor onset in real time, and physically braces the wrist at exactly the right moment — an on-demand biological stabilizer.

**HK angle:** HK's aging population has high essential tremor prevalence; assisted living facilities are chronically understaffed.

**Feedback:** Too hard to implement in 24h.

### Bin Enforcer

**Key idea:** Robot watches what a person drops via camera and physically intercepts mis-sorted waste mid-drop, redirecting it to the correct bin.

**HK angle:** HK's MSW levy creates financial incentive for correct sorting; contaminated bins incur fines building managers want to avoid.

**Feedback:** Interception mechanic is gimmicky; a simple sorter is better.

### Portrait Engraver

**Key idea:** Claude Vision analyzes a face and directs the robot to scratch a portrait into clay/wax using a fine stylus — AI perception translated into a permanent physical artifact.

**HK angle:** HK's tourist footfall and gift culture makes personalized instant keepsakes high-margin.

**Feedback:** Robotic arm is overkill; an ad-hoc device is better suited.

### Titration Proxy

**Key idea:** Robot drips reagent drop-by-drop while Claude Vision monitors color change and stops the arm at the exact endpoint — replacing a trained technician's eye-hand coordination.

**HK angle:** HK's food safety and water quality labs run high volumes of routine titrations.

**Feedback:** Ad-hoc dispenser device is simpler; the arm adds no value.

### Wet Stamp Sommelier

**Key idea:** Robot dips a sponge stamp pad with calibrated pressure to pick up exactly the right ink load, tests it on a scrap strip while Claude Vision reads print density, and iterates until ink transfer is perfect before executing the final stamp.

**HK angle:** TCM shops, wet markets, and hawker stalls across HK still price and label goods with inked chop stamps — inconsistent ink is a daily nuisance zero vendors have automated.

**Feedback:** Useless.

### Thread Tension Ghost

**Key idea:** Robot holds a sewing needle and pulls thread through fabric while Claude Vision reads the stitch pattern forming on the underside — motor torque feedback detects tension variance stitch-by-stitch, and the arm micro-adjusts pull speed in real time to produce perfectly uniform tension.

**HK angle:** Sham Shui Po garment workshops on razor margins lose entire batches of luxury fabric to tension defects rejected by buyers.

**Feedback:** Too difficult to implement; requires dexterous manipulation.

### Torque Notary

**Key idea:** Robot presses a pen onto paper and signs a contract field using a learned imitation trajectory, while motor torque feedback detects paper resistance variance and aborts before completing an invalid stamp — the arm refuses to sign until the physical setup is correct.

**HK angle:** HK's property agency and legal sector produces hundreds of physical contract signings daily; a misplaced wet signature on a deed triggers costly re-execution.

**Feedback:** Writing is too difficult.

### Blind Barista

**Key idea:** Robot tamps espresso grounds with calibrated force; motor torque feedback detects uneven resistance across the puck and re-tamps at soft spots until resistance is uniform — a level puck without human feel or visual inspection.

**HK angle:** HK's hyper-dense micro-café scene has new baristas producing inconsistent shots; a self-correcting tamper cuts the skill barrier for endless new openings.

**Feedback:** Not enough value.

### Ghost Shopper

**Key idea:** Robot arm mimics a customer's reach-and-grasp motion while Claude Vision maps which products are repeatedly reached for then put back — physical interaction as a customer research instrument no camera alone can capture.

**HK angle:** HK's cramped convenience and pharmacy chains have zero floor space for mystery shoppers; this produces a hesitation heatmap that informs restocking overnight.

**Feedback:** Useless.

### Grip Calibrator

**Key idea:** Robot offers its end-effector as a resistance handle; patient squeezes it while Claude logs force-over-time via motor current, compares against prior sessions, and physically adjusts resistance in real time to keep the patient in the therapeutic target zone.

**HK angle:** HK's overwhelmed public physiotherapy system has months-long waiting lists; a bedside device running unsupervised grip rehab for post-stroke elderly in subdivided flats fills a direct gap.

**Feedback:** Discarded.

### Score Keeper
**Key idea:** Robot reads a handwritten test paper with Claude Vision and physically circles errors with a pen — producing a teacher-graded sheet with zero human grader involvement.
**HK angle:** HK tutoring centers grade thousands of practice sheets per week; same-night physical graded return at zero labor cost is an immediate commercial hook.
**Feedback:** Arm is overkill, not really helpful.

### Tuning Ghost
**Key idea:** Robot turns a stringed instrument's tuning peg while a microphone feeds pitch to Claude — arm stops exactly at target frequency, self-tuning with no human ear needed.
**HK angle:** HK Cantonese opera and youth music education scenes have thousands of self-learners blocked by tuning as the first barrier to practice.
**Feedback:** Overkill.

### Freshness Prober
**Key idea:** Robot dips a thin probe into raw fish or tofu, reads motor resistance as a texture signature, and classifies freshness in real time — the arm's own motors as a food texture instrument.
**HK angle:** HK wet market vendors make daily freshness calls by hand-feel; a calibrated score removes subjective human judgment driving food poisoning complaints and stock loss.
**Feedback:** Requires sensors, not interesting.

### Counterfeit Cracker
**Key idea:** Robot drags a probe across a banknote or luxury tag at constant speed; Claude Vision watches the surface while motor torque detects micro-texture — two fused signals catch fakes that fool either sense alone.
**HK angle:** HK luxury goods and cash-heavy trading hub; counterfeit detection at point of sale is still done by eye and UV lamp.
**Feedback:** Not interesting.

### Wok Whisperer
**Key idea:** Claude Vision watches a wok and detects the exact oil shimmer/smoke point — arm drops pre-loaded ingredients at the precise moment, replacing the chef's split-second visual judgment.
**HK angle:** Cha chaan tengs and dai pai dongs run wok stations at brutal throughput; perfect wok hei timing takes years to learn and seconds to ruin a dish.
**Feedback:** Overkill.

### Page Turner
**Key idea:** Robot watches a reader's eye gaze via Claude Vision — when it detects the reader has finished the last line, arm physically turns the page, giving motor-disabled users hands-free reading with no book modification.
**HK angle:** HK's aging and disabled population has limited assistive tech options; works with any physical book, menu, or form in cramped home settings where tablet holders don't fit.
**Feedback:** Interesting but not good enough.

### Scan Sculptor
**Key idea:** Claude Vision analyzes a 3D scan in real-time, identifies occluded or low-confidence surfaces, and directs the arm to reposition the object to the exact angle that fills the gap — robot actively closes its own perceptual blind spots until a complete mesh is achieved.
**HK angle:** HK's cross-border e-commerce and luxury resale market requires accurate 3D product scans; turntable scanners leave systematic occlusion artifacts that sellers manually patch.
**Feedback:** In the right direction.

### Label Liberator
**Key idea:** Claude Vision tries to OCR a barcode or QR code — if it fails due to wrinkle, tear, or angle, the arm physically smooths, stretches, or tilts the packaging until the code becomes machine-readable. The robot fixes the physical world to unblock the software.
**HK angle:** HK logistics hubs process millions of deformed labels daily; failed scans are the single biggest throughput bottleneck in last-mile delivery operations.
**Feedback:** In the right direction.
