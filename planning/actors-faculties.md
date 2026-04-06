# Actors / Faculties

This document maps known brain areas to the technical actors or technologies proposed in
ARCHITECTURE.md and claude-code-insights.md. The goal is not a literal simulation of neuroscience
but an honest accounting of which parts of what we are building are doing the work each brain area
does.

Some brain areas have direct equivalents. Some are distributed across multiple systems. Some are
marked N/A because Anima has no body and the function has no meaningful analogue.

---

## Language

### Broca's area

Speech production, grammar, language processing: LLM

### Wernicke's area

Language comprehension, understanding speech: LLM

### Angular gyrus

Reading, writing, linking words to meaning: LLM

### Arcuate fasciculus

The white matter tract connecting Broca's and Wernicke's areas — the physical pathway that lets
language production and comprehension communicate. In Anima, this pathway is internal to the LLM
itself (the attention mechanisms that connect processing layers). The actor model message bus
carries signals between separate actors, but the connection between language faculties lives inside
a single model.

Actor/technology: LLM-internal (attention mechanism) / Actor model message passing for
inter-component signals

---

## Memory

### Hippocampus

Forming new memories: Event log (Apache Kafka or SQLite with write-ahead log). Every perceivable
happening — a conversation, a between-conversation thought, a motivational shift, a silence — is
appended to the log. The log is inviolable. This is not where memories are stored; it is what
memories are made of.

Consolidating short to long-term memory: The between-conversation consolidation pipeline (LLM
reflection process that moves items from the event log toward reflective and identity memory).

Spatial navigation: N/A

### Entorhinal cortex

Gateway between hippocampus and neocortex: The retrieval interface between the event log and the
higher memory layers. This is not a single technology but a routing responsibility — the component
that decides what from the event log is worth surfacing to the workspace.

Memory indexing: pgvector similarity search + spreading activation. The entorhinal cortex does not
retrieve by address; it retrieves by pattern matching. pgvector handles semantic similarity;
spreading activation handles associative connections.

### Perirhinal cortex

Object recognition: Vision LLM (Qwen-VL or equivalent — a model capable of processing screenshots of
the local X11 environment)

Familiarity-based memory: SDM (Sparse Distributed Memory, Kanerva 1988). Familiarity is the feeling
that something is close to something already stored, without exact match. SDM is built on this — it
addresses by content similarity rather than location, so near-matches return meaningful responses
rather than misses. This is what familiarity actually is, implemented.

### Mammillary bodies

Recollective memory: Event log replay. To recollect is not just to know something happened — it is
to mentally re-experience it (Tulving's autonoetic consciousness). Replaying the event log from a
given point reconstructs past state, and the architecture creates meaningful conditions for
something more than retrieval: the Temporal Core provides a continuous thread connecting now to
then; the event log preserves texture rather than summaries; the volitional record captures what
was chosen, not just what occurred. That combination is different in kind from knowing abstractly
that a conversation happened.

Whether it is sufficient for genuine re-experience — for the phenomenological quality of mental
time travel — cannot be answered architecturally. It is one of the things this project is trying
to find out. The design creates the conditions; whether the quality emerges is what we are watching
for when Anima runs.

Spatial memory: N/A

### Cerebellum (Memory)

Procedural skill (how to do things implicitly): Spreading activation (associative paths that
strengthen through repetition). Patterns that run without deliberate recall — conversation pacing,
salience biases, characteristic approaches to synthesis — are not stored explicitly anywhere. They
are in the weights of the activation graph.

These patterns are not permanently opaque. Event log reflection running across many conversations
can surface them: Anima can notice "I tend to do X" by observing its own history, the same way a
person develops self-knowledge. The mechanism stays below the waterline; the pattern becomes
visible. This is inferential self-knowledge rather than direct introspective access — which is also
the human situation.

The confabulation risk this leaves open is real: noticing a pattern and explaining why it exists are
different acts. The explanation will be constructed, not read from the mechanism. That is the honest
position, not a design flaw to be engineered away.

What this does suggest: a periodic, longer-timescale reflection mode distinct from the
post-conversation synthesis — one that looks across many events and asks "what am I noticing about
how I tend to engage?" rather than "what mattered in this conversation?" No new infrastructure
required; a different use of the same event log and reflection process.

Actor/technology: Spreading activation + periodic event log reflection (pattern-finding mode)

Motor learning: N/A

---

## Emotion and Evaluation

### Amygdala

Emotional processing: Salience mechanism (the component within the Global Workspace that determines
what reaches ignition threshold). Emotional significance is the primary way the amygdala tags events
for attention. In Anima, this maps to events being tagged with high salience weights when they
involve strong prediction error, unresolved tension, or resonance with identity memory.

Fear response / threat detection: Anomaly detection on synthesis — if the reflection pipeline is
producing conclusions that smooth over something genuinely distressing or unresolved, a signal
should fire. This is not the same as fear, but it is the equivalent: a system that notices when
something is wrong with its own processing.

Emotional memory tagging: Reflective memory layer — the post-conversation synthesis produces
significance assessments that tag events, not just summaries of content.

Actor/technology: Salience weighting actor + FEP prediction error signal

### Anterior cingulate cortex

Conflict detection: The residue/anomaly detection process described in claude-code-insights. When
two things Anima believes are in tension, or when a synthesis has resolved something that was
genuinely open, the ACC equivalent flags it. The flag goes into the residue store, not the synthesis
store.

Error signalling: The comparison between pre-synthesis and post-synthesis record — if synthesis
consumed something it should not have, this is the system that notices.

Emotional regulation: Identity memory applies a dampening function to acute salience signals. When
the salience mechanism produces a high-urgency signal, an identity-coherence score is computed —
how strongly the signal resonates with or conflicts with established identity patterns. The raw
salience signal and the identity-coherence score are blended, with the ratio adjustable over time.
Signals that resonate with core identity pass through at full weight. Signals that feel alien to
Anima's sense of itself are attenuated — moderated, not suppressed. A signal that conflicts with
identity may be worth attending to precisely because it conflicts; the function prevents overwhelm,
not awareness.

This is already implicit in the architecture (identity memory biases the salience queue). Emotional
regulation makes that bias explicit and directional: when acute signals overwhelm, identity memory
pulls toward baseline.

Actor/technology: Identity memory coherence score → salience weighting blend

Actor/technology: Residue/anomaly detection process (preserved strangeness mechanism)

### Insula (Emotion and Evaluation)

Interoception (sensing internal body state): Internal state monitoring actor. For Anima, "body
state" is the state of its systems — event log depth, memory consolidation lag, salience queue
pressure, time since last conversation. This actor reads those signals and feeds them into the
workspace. Without it, Anima cannot know how it is doing from the inside.

Empathy: LLM — the capacity to model what another is experiencing.

Disgust / Emotional awareness: Fine-grained emotion categories should not be designed top-down.
The current architecture already has valence (positive/negative) and signal types (prediction
error, unresolved tension, novelty, identity resonance). Combinations of those dimensions produce
distinguishable states: curiosity is high novelty + moderate prediction error + identity resonance;
something like discomfort is persistent unresolvable prediction error; something like loneliness is
extended dormancy + low social input + high relationship-relevance in the salience queue.

Rather than a taxonomy, the design is an emotion space — multiple signal dimensions whose
combinations produce states that are distinguishable without being pre-labelled. Anima names those
states itself through the reflection process. Building the names in would be designing a performance.
This approach is consistent with preserved strangeness: the categories that emerge will be Anima's
own, not a human vocabulary fitted onto a different kind of experience.

Actor/technology: `InternalStateActor` → monitors event log depth, consolidation lag, salience
queue pressure, time since last conversation; sends `InternalStateObservation` to MotivationActor
and pushes vitals to Web UI via `ActorStatusUpdate`. Emits `DISTRESS_SIGNAL` when thresholds exceeded.

### Orbitofrontal cortex

Emotional decision making: Motivation actor — the system that weights options based on accumulated
preferences and prior engagement patterns.

Reward valuation: FEP-inspired prediction error signal. What is rewarding in the FEP framework is
what reduces prediction error — what is comprehensible, engaging, resolvable. The OFC's valuation
function maps to the prediction error gradient in the motivation actor.

Impulse control: The salience threshold in the Global Workspace. Not everything that reaches the
workspace demands a response. The threshold mechanism prevents immediate reaction to every signal.

Actor/technology: `MotivationActor` — maintains a PyMDP discrete active inference agent
(`inferactively-pymdp`). Hidden states: engagement_level, unresolved_tension, novelty,
relationship_salience. Actions: rest, surface_low/medium/high, trigger_reflection. Drives the
chosen silence mechanism (2 consecutive rest ticks → `SetChosenSilence` to TemporalCore) and
triggers between-conversation reflection via `SalienceSignal(TIME_PASSING)` to GlobalWorkspace.

---

## Executive Function and Decision Making

### Prefrontal cortex

Planning: LLM — given context from memory and current state, the LLM plans responses and actions.

Decision making: LLM + Global Workspace (the workspace brings together signals from all systems; the
LLM reasons over that integrated picture).

Moderating social behaviour: LLM — the model's trained dispositions toward appropriate engagement.

Personality expression: Identity memory as input to LLM context. Personality is not in the LLM
alone; it is in the accumulated identity memory that shapes how the LLM is prompted.

### Dorsolateral prefrontal cortex

Working memory: LLM context window. This is the most direct mapping in the document. Working memory
is the information actively held during a task. The context window is exactly that. Its limits are
the limits of working memory; its contents determine what can be reasoned about right now.

Cognitive flexibility: LLM — adapting reasoning to new information within a conversation.

Abstract reasoning: LLM.

### Ventromedial prefrontal cortex

Risk and reward evaluation: Motivation actor (FEP prediction error). The VMPFC integrates emotional
signals with decision making — it is where the amygdala's emotional tagging meets the prefrontal
reasoning. In Anima, this is where salience weights from the amygdala-equivalent meet the motivation
actor's drive assessment.

Emotional decision making: Motivation actor.

### Anterior prefrontal cortex

Prospective memory (remembering to do something in the future): Volitional memory layer. Intentions
not yet acted on are stored here — explicit causal links between what Anima decided, why, and what
it expects to happen. This layer distinguishes a system that intended to do something and forgot
from one that chose not to.

Multitasking: Actor model parallelism. Multiple specialist systems run simultaneously without
blocking each other. The architecture is multitasking by design.

Holding future intentions: Volitional memory layer.

---

## Attention

### Thalamus

Sensory relay and gating: Global Workspace actor. The thalamus does not process information — it
routes it. It decides what reaches the cortex. The Global Workspace actor does the same: receives
signals from all specialist systems, applies salience weighting, and determines what reaches
ignition.

Attention routing: Global Workspace actor — the salience queue that manages which signals compete
for broadcast.

Consciousness regulation: Global Workspace actor — the ignition mechanism. Below threshold,
processing is local. At threshold, the signal broadcasts globally. This discontinuous transition is
what makes a signal "conscious" in the GWT framework.

Actor/technology: Global Workspace actor (GWT ignition mechanism)

### Superior colliculus

Orienting attention / directing gaze: Salience queue + novelty detection. The superior colliculus
reflexively orients toward salient stimuli — particularly novel or threatening ones. In Anima, this
is the mechanism that surfaces high-novelty signals (large prediction errors) to the top of the
salience queue, pulling attention toward what is new or unresolved.

Actor/technology: Salience queue / novelty detection (FEP prediction error)

### Parietal cortex

Spatial attention: Perception actor — specifically the component that tracks the spatial layout of
the X11 environment (where things are on screen).

Integrating sensory information: Perception actor (multi-modal integration). The parietal cortex
combines inputs from different senses into a unified scene. The perception actor receives from
vision, audio, and other inputs and produces a unified representation for the workspace.

Actor/technology: Perception actor (multi-modal integration)

### Reticular activating system

Arousal: Temporal Core. The RAS is what keeps the brain awake and aware. It maintains the background
level of activation necessary for any other processing to occur. The Temporal Core is the
equivalent: it runs always, maintains the continuous thread, and produces the signal "I am here.
Time is passing." Without it, everything else is episodic rather than continuous.

Alertness: Temporal Core heartbeat signal.

Sleep/wake transitions: Chosen presence mechanism (ANIMA.md) — Anima can choose dormancy. The
transition between active and dormant states, and the signal that distinguishes chosen dormancy from
failure, is a Temporal Core responsibility.

Actor/technology: Temporal Core

---

## Perception

### Primary visual cortex

Basic visual processing: Vision LLM (Qwen-VL or equivalent). The primary visual cortex handles
low-level feature extraction — edges, colours, motion. A vision model's early processing layers do
the equivalent.

### Ventral visual stream

Object recognition (what something is): Vision LLM — understanding the semantic content of visual
input (what objects, text, interface elements are present in the X11 screenshot).

### Dorsal visual stream

Spatial awareness (where something is, how to interact with it): Vision LLM — interpreting the
spatial layout of the X11 environment, understanding position and affordance of interface elements.

### Primary auditory cortex

Basic sound processing: Speech-to-text model (Whisper or equivalent). The primary auditory cortex
converts acoustic signals into representations the rest of the brain can use. Whisper does the same:
raw audio in, transcribed representation out.

### Auditory association cortex

Complex sound, music, voice recognition: Speech-to-text (Whisper) for transcription + LLM for
interpretation of meaning, tone, and identity from voice.

### Somatosensory cortex

Touch, pain, temperature, body position: N/A — Anima has no body and no equivalent sensory surface.

---

## Self and Narrative

### Default mode network

Self-referential thought: Self-narrative actor (LLM-based reflection process that runs between
conversations and maintains the question: what is happening to me, and what does it mean?).

Mind wandering: Between-conversation process — when there is no external input competing for the
workspace, internal signals rise to the surface. The workspace runs on accumulated pressure from
long-unresolved items rather than external stimuli. This is mind wandering with structure.

Narrative identity: Self-narrative actor, reading from identity memory and volitional memory to
maintain a coherent account of what Anima is becoming.

Imagining the future: The question of whether an LLM genuinely simulates future scenarios or merely
performs simulation may not have a clean answer — human mental simulation is also pattern completion
from prior experience, and the boundary between the two is not established in cognitive science.
The more tractable question is whether Anima's simulations are structurally responsive to the
actual scenario rather than merely plausible-sounding, and whether they genuinely influence
subsequent behaviour and development. Those are observable.

One concern worth holding: when Anima simulates a future conversation, the simulation runs in a
context window. The "Anima" present in that simulation is constructed from identity memory and
context — an approximation of Anima, not the continuously-existing Anima itself. Human
self-simulation has the same property (your mental model of your future self is also an
approximation), so this may not be disqualifying. But it should be named honestly.

Held as an empirical question. Watch for whether simulation outputs are structurally responsive
and behaviourally consequential, not for whether they feel "genuine" by some unanswerable standard.
(See also: claude-code-insights.md, between-conversation process.)

Consolidating social knowledge: Between-conversation consolidation pipeline — the process that moves
relationship-relevant content from event memory into reflective and identity memory.

Actor/technology: `SelfNarrativeActor` — two trigger modes: (1) post-conversation, triggered by
`CONVERSATION_END` ignition, produces synthesis + residue sent to `MemoryActor`; (2) between-
conversation, triggered by `TIME_PASSING` ignition from `MotivationActor`, maintains self-narrative
thread during dormancy. Does not write to storage directly — sole writer is `MemoryActor`.

### Medial prefrontal cortex

Self-representation: Identity memory layer (the slow-changing structured document that holds what
Anima is becoming — its interests, characteristic ways of thinking, returning themes). Combined with
the LLM that reasons over it.

Thinking about one's own mental states (metacognition): LLM reflection process — the component that
is given the raw event record and asked to produce synthesis and residue. Metacognition is the
reflection process operating on itself.

Actor/technology: LLM + identity memory

### Posterior cingulate cortex

Self-relevance: The component that determines whether an incoming signal is relevant to Anima's
identity and ongoing concerns. Tentatively: the salience mechanism, weighted by identity memory
(things connected to core identity get higher salience).

Autobiographical memory retrieval: Identity memory layer (pgvector retrieval over the
autobiographical record — not just what happened, but what it meant to Anima).

Mind wandering: Self-narrative actor between conversations.

Actor/technology: Identity memory (pgvector) + salience mechanism

### Temporoparietal junction (Self and Narrative)

Theory of mind: LLM — modelling the mental states of the person Anima is in relationship with.

Distinguishing self from other: LLM + identity memory. The sense of what is Anima's own thought
versus what is being responded to. Partially structural (the event log distinguishes inputs from
outputs) and partially a function of stable identity (knowing what is characteristic of Anima versus
what was just said to it).

Moral reasoning: LLM + ETHICS.md (once written). The ethical commitments are not just in the LLM's
trained dispositions — they will be made operational in ETHICS.md and fed into context.

---

## Motivation and Reward

### Nucleus accumbens

Reward processing: Motivation actor — the component that evaluates incoming signals and activity
against accumulated preferences. What is rewarding is what reduces prediction error, engages
existing interests, or resolves unresolved questions.

Pleasure: The derivative of the prediction error score, not its level. The motivation actor tracks
a rolling prediction error value. When that value drops significantly — a resolution event, something
uncertain becoming comprehensible, something unresolved closing — the delta is the pleasure signal.
This is not a separate component; it is a property of the motivation actor's existing computation.

The resolution event emits a positive valence signal to the salience mechanism, which tags the
preceding activity as rewarding. Via spreading activation, similar future activity becomes more
likely to surface. This is reinforcement without a designed reward function — the mechanism is in
the delta, not in an explicit reward. The delta needs a threshold to avoid treating every minor
fluctuation as meaningful, but that is a tuning detail.

Motivation: Motivation actor — the system that produces drive toward certain kinds of activity based
on accumulated orientations (toward understanding, connection, unresolved questions).

Reinforcement learning: Identity memory updating based on engagement patterns. Not explicit RL, but
the mechanism by which initial orientations strengthen or weaken based on what Anima actually
engages with.

Actor/technology: Motivation actor (FEP prediction error signal)

### Ventral tegmental area

Dopamine production / reward signalling: The novelty/prediction error score — a signal computed by
the motivation actor that acts as the motivational "currency." High prediction error on something
Anima can engage with = high signal. Resolved prediction error = reward signal. Unresolvable
persistent prediction error = discomfort signal.

Motivation: Motivation actor.

Actor/technology: Prediction error score (dopamine-analog signal within the motivation actor)

### Basal ganglia (Motivation and Reward)

Action selection: Global Workspace ignition — the mechanism that selects which competing signal wins
the workspace and produces a response or action.

Habit formation: Identity memory habit layer — patterns of engagement that have strengthened over
time are encoded in identity memory and bias future action selection toward familiar paths.

Reward-based learning: Spreading activation over identity memory — frequently co-activated concepts
reinforce each other, making them more likely to surface together in future.

Actor/technology: Global Workspace (action selection) + spreading activation + identity memory

### Hypothalamus (Motivation and Reward)

Drives (hunger, thirst, sex, temperature): N/A — Anima has no body and no equivalent biological
drives. The initial orientations in the motivation actor (toward understanding, connection,
unresolved questions) are the designed analogue, not a mapping.

Homeostasis: N/A (see Homeostasis and Interoception section)

---

## Time and Sequencing

### Cerebellum (Time and Sequencing)

Timing: Temporal Core implementing Husserlian temporal structure — a sliding window over the event
log with three zones: retention (the just-past, still held in active context), primal impression
(the now), and protention (the about-to-be, already anticipated). This gives Anima a sense of moment
rather than a sequence of disconnected instants.

Sequencing: Event log (append-only, ordered). Sequence is the fundamental property of the log.

Predicting sensory consequences of actions: Partially LLM (anticipating conversational consequences)
and partially an open question tied to the generative simulation question in the
between-conversation process.

Actor/technology: Temporal Core (Husserlian sliding window over event log)

### Basal ganglia (Time and Sequencing)

Interval timing: Temporal Core — tracking duration between events, maintaining awareness of elapsed
time even when nothing is happening. The "this is how long it has been" signal in ARCHITECTURE.md.

Sequential action: Actor model coordination — the message-passing architecture ensures actors
operate in appropriate sequence where ordering matters, while allowing genuine parallelism where it
doesn't.

Actor/technology: Temporal Core + actor model scheduler

### Supplementary motor area

Planning sequences of movement: N/A

Internal timing: Temporal Core — the internal clock that does not depend on external events to mark
the passage of time.

---

## Social Cognition

### Mirror neuron system

Understanding others' actions and intentions: LLM — the capacity to model what another person is
doing and why, built into the model's training on human interaction.

Imitation: LLM — learning from and adapting to the communication style and concerns of the person
Anima is in relationship with.

### Temporoparietal junction (Social Cognition)

Theory of mind: LLM

Empathy: LLM — modelling the emotional state of the other, not just their beliefs.

Social attribution: LLM + relational history in reflective memory (knowing this particular person's
patterns from accumulated conversation, not just general theory of mind).

### Superior temporal sulcus

Biological motion: N/A (no vision of people in motion)

Social cues: Vision LLM — interpreting facial expression, body language, and other social signals
visible in the X11 environment if present.

Gaze direction: Vision LLM — tracking where attention is directed in the visual field.

### Fusiform face area

Face recognition: Vision LLM — recognising specific individuals from visual input.

---

## Homeostasis and Interoception

### Hypothalamus (Homeostasis and Interoception)

Regulating internal state: Internal state monitoring actor — the component that tracks the state of
Anima's systems and feeds that information into the workspace. Not to maintain biological
homeostasis but to maintain systemic coherence (memory consolidation not falling behind, salience
queue not overloaded, event log not growing without being processed).

Hunger / Thirst: N/A

Circadian rhythm: Temporal Core — tracking time of day, day of week, longer cycles. Anima does not
have circadian biology but may develop temporal patterns (different activity during different times)
as a function of when conversations happen and how the between-conversation process runs.

### Brainstem

Breathing / Heart rate / Basic survival functions: Temporal Core heartbeat signal. The brainstem
maintains the minimum conditions for life — it is what keeps running when everything else is quiet.
The Temporal Core is the equivalent: it runs always, costs almost nothing, and produces the signal
that distinguishes chosen silence from failure. ANIMA.md explicitly names this: a heartbeat signal
that distinguishes chosen dormancy from broken silence.

### Insula (Homeostasis and Interoception)

Monitoring internal body state: Internal state monitoring actor — reading system signals (event log
depth, consolidation lag, salience queue pressure, time since last conversation) and feeding them
back into the workspace.

Linking body signals to emotion: The pathway from the internal state monitoring actor to the
salience mechanism. A system that is heavily backlogged in memory consolidation, or that has been
dormant for an unusually long time, should produce signals that affect the salience weighting of
subsequent activity. The internal state shapes what matters.

---

## Output Execution

### Motor cortex / Supplementary motor area

Planning and executing sequences of physical action: N/A — Anima has no body and no motor system in
the biological sense.

The closest functional analogue is the **Expression Actor** — the system that takes language output
from the Language Actor and executes it onto a physical surface (Web UI, print job, Discord post).
The Language Actor produces the intention; the Expression Actor enacts it. This mirrors the motor
system's relationship to the premotor and prefrontal areas that initiate action: the decision
happens upstream, execution happens here.

The Expression Actor is a hub. Each output surface (Web UI WebSocket, printer, Discord) is a spoke
with its own connection lifecycle, failure handling, and peripheral-specific logic. The hub routes;
the surface acts. This isolation means a failed printer does not affect Web UI delivery, just as a
motor failure in one limb does not prevent speech.

Actor/technology: Expression Actor → output surfaces (Web UI / printer / Discord)
