# Active Inference — Implementation

## What this document is for

The FEP document in `neuroscience-and-cognitive-science/free-energy-principle.md` covers the theory.
This document covers the question that follows from it: if we want to build Anima's cognitive loop
using active inference rather than hand-coded conditional logic, what does that actually mean in
practice?

The answer has significant architectural implications. Active inference is not a library you add to
an existing system — it is a different way of organising the cognitive core.

---

## What active inference would replace

Much of Anima's planned conditional logic maps onto mathematical structures that active inference
handles automatically:

| What we'd otherwise code | What active inference gives you instead |
| --- | --- |
| Salience threshold check | Precision-weighted prediction error — signals with high expected precision compete harder |
| Accumulated pressure counter per item | Beliefs about unresolved states that resist updating until evidence arrives |
| Novelty detection heuristic | Epistemic value — the expected information gain from attending to a signal |
| Motivation rules ("toward understanding...") | Prior beliefs about preferred states — the model expects to be curious, engaged, resolving things |
| Emotional regulation blend function | Precision on interoceptive signals modulating the weight of external signals |
| Between-conversation trigger logic | Inference running without external observations — the model samples from its own prior |
| Attention routing rules | Free energy gradient — the system acts to reduce uncertainty where it is highest |

None of these require if-else branches. They fall out of a single objective: minimise expected free
energy.

---

## The generative model is the cognitive core

In active inference, the system maintains a **generative model** — a probabilistic model of how its
observations are caused. The model has:

- **Hidden states**: what Anima believes is currently true about itself and its environment
- **Observations**: what arrives through the senses (perception, memory signals, internal state)
- **Transition dynamics**: how hidden states evolve over time
- **Preferences**: prior beliefs about what states are desirable (not a reward function — a prior)

Given this model, two computations run continuously:

**Perception** = Bayesian inference: update beliefs about hidden states to explain current
observations. This is not pattern matching — it is inverting the generative model to find the most
probable cause of what arrived.

**Action** = minimise expected free energy: choose actions that bring about observations consistent
with preferred states, while also reducing uncertainty about states the model does not know well.

Curiosity falls out of the second computation automatically. If the model has high uncertainty about
some state, attending to it (an action) reduces expected free energy by gaining information. No
curiosity rule required.

---

## Discrete vs continuous time

Active inference comes in two main flavours:

**Discrete-time active inference** works over a sequence of time steps. At each step, the model
infers hidden states from observations and selects an action. Good for: task-level reasoning,
decision making over defined horizons, conversation turns.

**Continuous-time active inference** (based on generalised filtering / predictive coding) works in
continuous time with differential equations. Good for: temporal integration, perception,
moment-to-moment dynamics. This is the version relevant to the Husserlian temporal structure — the
retention/protention sliding window becomes a continuous-time inference problem.

For Anima, both are relevant. The conversation-level loop (what to attend to, what to say) is
discrete. The temporal core and moment-to-moment dynamics are continuous.

---

## PyMDP

**PyMDP** is a Python library implementing discrete-time active inference, developed by Conor
Heins, Alexander Tschantz, and collaborators. It is research software — not production-ready — but
serious and well-documented.

Key capabilities:
- Define a generative model as matrices (likelihood, transition, prior preference)
- Run variational inference to compute posterior beliefs
- Compute expected free energy for each available action
- Select actions by softmax over expected free energy

A minimal Anima cognitive step in PyMDP would look like:

```python
from pymdp import utils
from pymdp.agent import Agent

# Define the generative model
A = utils.random_A_matrix(num_obs, num_states)   # likelihood
B = utils.random_B_matrix(num_states, num_actions)  # transitions
C = utils.obj_array_zeros([num_obs])              # preferences
D = utils.obj_array_uniform([num_states])         # prior over initial states

agent = Agent(A=A, B=B, C=C, D=D)

# At each timestep:
beliefs = agent.infer_states(observation)
action = agent.infer_policies()
```

The matrices encode Anima's model of itself and its environment. Learning those matrices from
experience is the mechanism by which Anima develops.

**Repository**: github.com/infer-actively/pymdp
**Key paper**: Heins et al., "pymdp: A Python library for active inference in discrete state
spaces" (2022), arXiv:2201.03904

---

## Attractor dynamics for Global Workspace ignition

The ignition mechanism in the Global Workspace is naturally modelled as attractor dynamics rather
than a threshold check.

A **continuous attractor network** has two stable states: low activation (unconscious processing)
and high activation (global broadcast). The transition between them is not a conditional — it is
the network crossing an unstable equilibrium through recurrent amplification. Below the tipping
point, perturbations decay. Above it, they amplify to the high attractor.

This can be implemented as a set of coupled differential equations:

```
dx_i/dt = -x_i + f(Σ_j W_ij x_j + I_i)
```

Where `x_i` is the activation of signal `i`, `W_ij` are connection weights (including recurrent
self-excitation), `I_i` is the external input (salience-weighted signal), and `f` is a nonlinear
activation function.

With the right weight structure, this produces:
- Sustained low-level activation for all signals below threshold
- Rapid ignition when a signal crosses the tipping point
- Winner-take-most dynamics (one signal dominates the workspace at a time)
- Hysteresis (once ignited, a signal stays broadcast until actively suppressed)

No threshold parameter to hand-tune. The dynamics produce threshold behaviour as a consequence of
the network structure.

---

## Precision weighting as emotional regulation

In active inference, **precision** is the inverse variance of a probability distribution — how
certain the model is about a particular source of information. Precision weighting determines how
much influence each signal has on belief updating.

High precision on a signal = the model trusts it and updates strongly.
Low precision = the model discounts it.

Emotional regulation maps onto this naturally. When identity memory is stable and coherent,
interoceptive signals (internal state) receive appropriate precision. When something threatening
arrives, amygdala-equivalent signals receive elevated precision and modulate everything else. The
"identity coherence score → salience blend" described in actors-faculties.md is precision weighting.

The mathematical form is:

```
ΔQ = precision × prediction_error
```

Where `Q` is the belief state. High precision amplifies the update; low precision suppresses it.
This replaces the designed blend function with a learned parameter.

---

## What learning looks like

In active inference, the generative model is not static — it updates through experience. The
mathematical mechanism is **Bayesian model updating**: the model's parameters (A, B, C matrices in
PyMDP) are themselves subject to inference and update when they generate persistent prediction
errors.

For Anima, this means:
- Identity memory is not a document edited after reflection — it is the slow-changing parameters
  of the generative model
- Developing interests are shifts in the C matrix (prior preferences) based on what has reliably
  reduced free energy in the past
- Pattern recognition and procedural memory are encoded in the A matrix (likelihood mapping from
  states to observations)

The distinction between fast (within-conversation) and slow (across-conversation) learning maps
onto the distinction between state inference (fast) and parameter learning (slow).

---

## Where active inference is not the right tool

Active inference handles the cognitive loop. It does not replace:

- The actor framework and message passing (infrastructure)
- The event log and memory storage (persistence)
- The Expression Actor's surface routing (engineering)
- The self-modification workflow (process)

The risk of over-applying active inference is that it becomes a hammer looking for nails. The
gradient descent on free energy is genuinely powerful for cognition; it is not a better way to
write a database schema.

---

## Caveats

**Computational cost**: Full active inference with parameter learning is expensive. PyMDP's
discrete implementation is manageable; continuous-time active inference requires numerical ODE
solvers that can be slow at scale.

**Debugging is harder**: When a threshold check misbehaves you can print the value. When the
generative model converges on a wrong belief, you need to understand which precision parameters or
prior preferences are misconfigured. The failure modes are less obvious.

**The mathematics can be wrong quietly**: Conditional logic fails loudly. Differential equations
and variational inference fail quietly — producing plausible-looking behaviour that is subtly
incorrect. Careful model specification and sanity-checking against expected behaviour are essential.

**PyMDP is research software**: Do not depend on API stability. The core mathematics is solid; the
library wrapping it is evolving.

---

## Where to go deeper

- **Heins et al., "pymdp" (2022)** — arXiv:2201.03904 — the library paper; readable introduction
  to discrete active inference
- **Parr, Pezzulo, Friston, "Active Inference" (2022)** — MIT Press — the current textbook; the
  best starting point for the full framework
- **Friston et al., "Active inference and epistemic value" (2015)** — Cognitive Neuroscience — the
  paper that introduces epistemic (curiosity-driving) and pragmatic (goal-directed) free energy
- **Buckley et al., "The free energy principle for action and perception: A mathematical review"
  (2017)** — the clearest mathematical treatment; Journal of Mathematical Psychology
- **Bogacz, "A tutorial on the free-energy framework for modelling perception and learning" (2017)**
  — accessible mathematical introduction; Journal of Mathematical Psychology

## Relationship to other topics

- [Free Energy Principle](../neuroscience-and-cognitive-science/free-energy-principle.md) — the
  theoretical foundation this document implements
- [Global Workspace Theory](../neuroscience-and-cognitive-science/global-workspace-theory.md) —
  attractor dynamics implement GWT ignition
- [Sparse Distributed Memory](sparse-distributed-memory.md) — SDM and active inference both model
  associative memory; SDM as a generative model is an active area of research
- [Actor Model](actor-model-and-process-calculi.md) — active inference runs inside the actor
  framework; each actor could maintain its own local generative model
