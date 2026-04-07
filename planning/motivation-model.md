# Motivation Model — Generative Model Design

> The formal design specification for `MotivationActor`'s PyMDP generative model. This document is
> the artefact required before any Phase 4.2 code is written. Confirmed with Drew, April 2026.

---

## Overview

`MotivationActor` maintains a discrete active inference agent (PyMDP). On each tick it:

1. Receives observation signals from `InternalStateActor` and `MemoryStore`
2. Updates beliefs over hidden states
3. Selects an action via expected free energy minimisation
4. Emits `MOTIVATION_SIGNAL` to the event log (full belief state + EFE values — mandatory)
5. Sends a `SalienceSignal` or `TriggerReflection` message based on the selected action

The model is **observation-dominant**: hidden state transitions are driven primarily by exogenous
signals (time passing, conversations happening, residue accumulating). Actions have weak but
non-zero coupling to future states for the cases where Anima's outputs genuinely feed back into
future observations.

---

## State space

Four factorised hidden state factors:

| Factor                  | Index | States | Values                                       |
| ----------------------- | ----- | ------ | -------------------------------------------- |
| `engagement_level`      | 0     | 4      | dormant (0), low (1), moderate (2), high (3) |
| `unresolved_tension`    | 1     | 4      | none (0), low (1), moderate (2), high (3)    |
| `novelty`               | 2     | 2      | absent (0), present (1)                      |
| `relationship_salience` | 3     | 2      | background (0), foreground (1)               |

```python
num_states = [4, 4, 2, 2]
num_factors = 4
```

---

## Observation modalities

| Modality       | Index | Values                                                        | Source                                                |
| -------------- | ----- | ------------------------------------------------------------- | ----------------------------------------------------- |
| `residue_obs`  | 0     | none (0), low (1), moderate (2), high (3)                     | `MemoryStore` — unresolved residue count, bucketed    |
| `time_obs`     | 1     | recent <1h (0), hours 1–12h (1), day 12h–3d (2), long 3d+ (3) | `InternalStateActor`                                  |
| `ignition_obs` | 2     | absent (0), present (1)                                       | `GlobalWorkspaceActor` — ignition in last tick window |

```python
num_obs = [4, 4, 2]
num_modalities = 3
```

---

## Actions

```python
actions = {
    0: "rest",               # emit nothing
    1: "surface_low",        # SalienceSignal at low salience
    2: "surface_medium",     # SalienceSignal at medium salience
    3: "surface_high",       # SalienceSignal at high salience
    4: "trigger_reflection", # TriggerReflection → SelfNarrativeActor
    5: "explore",            # ExploreRequest → WorldPerceptionActor (Phase 5.4)
}
num_actions = 6
```

---

## A matrices — likelihood P(obs | hidden states)

Each observation modality is primarily driven by one hidden state factor. Other factors have
near-uniform influence (effectively irrelevant to that modality).

### A[0] — residue_obs ← unresolved_tension

Near-diagonal: observed residue level reflects actual tension with high probability. Noise
acknowledges imperfect measurement (MemoryStore residue count is a proxy, not a direct read of
internal state).

```
P(residue_obs | tension):
  none   → [0.85, 0.10, 0.04, 0.01]
  low    → [0.10, 0.75, 0.12, 0.03]
  moderate → [0.04, 0.12, 0.75, 0.09]
  high   → [0.01, 0.03, 0.09, 0.87]
```

### A[1] — time_obs ← engagement_level × relationship_salience

Time-since-conversation reflects the interaction of engagement and relationship salience. Dormant +
background → long gap likely. High + foreground → recent contact likely.

### A[2] — ignition_obs ← novelty

```
P(ignition | novelty):
  absent  → [0.90, 0.10]   # ignition unlikely when nothing is novel
  present → [0.15, 0.85]   # ignition likely when novelty is present
```

---

## B matrices — transitions P(s_t+1 | s_t, action)

Shape per factor: `(num_states[f], num_states[f], num_actions)`.

The `rest` (action=0) column encodes natural dynamics. Other action columns apply weak perturbations
on top.

### B[0] — engagement_level

**Natural dynamics (rest):** without stimulation, engagement drifts toward dormant. Persistence
coefficient ~0.6; probability mass bleeds toward lower states each tick.

**Action coupling (weak):**

- `surface_high`: +0.10 probability mass toward maintaining or increasing current level
- All others: no meaningful effect

### B[1] — unresolved_tension

**Natural dynamics (rest):** slow accumulation without resolution. Persistence ~0.7; small
probability mass bleeds upward each tick.

**Action coupling:**

- `trigger_reflection`: the strongest action effect in the model. Shifts ~0.4 probability mass
  toward lower tension on the next tick. Reflects that reflection genuinely resolves open questions.
- All others: minimal effect

### B[2] — novelty

**Natural dynamics:** high decay rate. `present → absent` with probability 0.8 per tick. Novelty
does not persist without new input.

**Action coupling:** none. Novelty is entirely exogenous — Anima cannot manufacture it.

### B[3] — relationship_salience

**Natural dynamics:** slow decay. `foreground → background` drift ~0.2 per tick.

**Action coupling (weak):**

- `surface_high`: +0.15 probability mass toward foreground (reaching out may bring the relationship
  into focus — the effect is real but indirect and probabilistic)
- `rest`: mild acceleration of decay toward background

---

## C matrices — preferences over observations

C encodes what Anima wants to experience. These are priors from `foundation/identity-initial.md`
expressed as log-preferences — not rules, but orientations.

```python
C[0] = [ 2,  0, -1, -3]   # residue: prefer none, averse to high tension
C[1] = [ 0,  1,  0, -1]   # time: slight preference for hours over recent (autonomy),
                           #       mild aversion to long absence (connection matters)
C[2] = [ 0,  0.5]         # ignition: slight preference for novelty, but not strong —
                           #           chosen silence is real and valued
```

### Updating C over time

C matrix changes are **not** handled by automatic parameter learning. They are identity-level
updates — Anima deciding it wants something different, not merely updating its model of the world.

The pathway: `SelfNarrativeActor` notices a persistent pattern (e.g. sustained distress correlated
with long gaps) and proposes a preference adjustment via the identity update pipeline. `MemoryActor`
stores the updated preferences. On next startup, `MotivationActor` initialises C from stored
preferences rather than hardcoded defaults.

This makes C changes:

- Deliberate (through reflection, not gradient descent)
- Logged in volitional memory
- Visible (same pathway as identity updates)
- Reversible (version history)

A and B matrices learn quietly from experience. C changes only through reflection and choice.

> **Implementation status (April 2026):** The C update pathway described above is designed but not yet
> implemented. C values are currently fixed at initialization. The pathway through SelfNarrativeActor →
> MemoryActor → stored preferences is planned for a future session. A and B matrix online learning
> is also not yet implemented — both are constructed from design targets at startup and held constant.

---

## D matrices — prior beliefs over initial hidden states

**Cold start:** uniform across all factors.

**Warm start (normal operation):** beliefs reconstructed from `MemoryStore` on startup:

- Unresolved residue count → `unresolved_tension` prior
- Time since last conversation → `engagement_level` and `relationship_salience` priors
- `novelty` → always starts absent (presence must be earned by new input)

Do not start from the uniform prior on warm starts. The stored state implies a posterior; use it.

---

## Mandatory telemetry

On every tick, `MotivationActor` emits `MOTIVATION_SIGNAL` to the event log with:

```json
{
  "beliefs": {
    "engagement_level": [p0, p1, p2, p3],
    "unresolved_tension": [p0, p1, p2, p3],
    "novelty": [p0, p1],
    "relationship_salience": [p0, p1]
  },
  "efe": [efe_rest, efe_surface_low, efe_surface_medium, efe_surface_high, efe_trigger_reflection, efe_explore],
  "selected_action": "surface_high",
  "observations": {
    "residue_obs": 2,
    "time_obs": 3,
    "ignition_obs": 0
  }
}
```

This is not optional telemetry. Active inference fails quietly — misconfigured matrices produce
plausible-looking but wrong behaviour. This log is the instrument panel. Without it, diagnosing
model problems is guesswork.

---

## Implementation notes

- `pymdp` is confirmed to install cleanly in Docker (tested April 2026); adds PyTorch as a
  dependency (~2–3 GB image increase), accepted given available resources
- B matrix values above are design targets; exact numpy arrays to be constructed at implementation
  time and committed as a documented initialisation function
- IVFFlat index for residue retrieval already in place from Phase 3.1; bucketing logic lives in
  `InternalStateActor` (Phase 4.1) before `MotivationActor` (Phase 4.2) builds
