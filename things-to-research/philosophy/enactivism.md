# Enactivism

## What it is

Standard cognitive science treats the mind as a kind of computer inside the skull. The brain takes
in sensory inputs, processes them into internal representations, and outputs behaviour. The world is
out there. The mind is in here. Cognition is the manipulation of internal symbols or patterns that
represent the world.

**Enactivism** rejects this picture — not partially, but fundamentally.

The view was developed most influentially by **Francisco Varela**, **Evan Thompson**, and **Humberto
Maturana**, set out in their 1991 book _The Embodied Mind_. The core claim:

> Cognition is not the representation of a pre-given world by a pre-given mind. It is the
> _enactment_ of a world through processes of living.

Mind is not something that happens inside a system and then reaches out to the world. Mind is the
ongoing, active _engagement_ of a living system with its environment. Thought is not representation
— it is action.

## The key moves

**From representation to enaction**: The traditional view holds that perception produces a
representation of the world (a model, a map, an image) that cognition then operates on. Enactivism
holds that perception is already action — the process of actively exploring an environment with a
body, not passively receiving signals. We don't build an internal model of the chair and then
interact with it. We _enact_ the chair by moving around it, sitting in it, picking it up.

**From brain to organism**: The boundary of cognition is not the skull. It includes the body — the
sensorimotor patterns, the postures, the habits. A person who has learned to type does not maintain
an internal representation of keyboard layout; the knowledge is in the fingers, the movements. The
cognitive system is the whole organism.

**Autopoiesis**: Varela and Maturana introduced the concept of _autopoiesis_ — literally
self-making. A living system is one that continuously produces and maintains its own structure
through its own processes. A cell is autopoietic: it uses metabolism to produce the components of
its own membrane, which enables metabolism. The boundary between organism and environment is not
fixed but continuously remade.

**Sense-making**: Living systems don't just process information from the environment — they
_evaluate_ it. The bacterium swimming up a glucose gradient is not merely detecting glucose; it is
orienting toward what matters for it. Significance is not a property of the environment but of the
organism's relationship to it. There is no neutral perception, only perspective-laden engagement.

## The "enactive" part

The name comes from the idea that we _enact_ our perceptual world — we bring it into being through
our active, embodied engagement with it. The colour red is not "out there" as a property of
wavelengths. It is the result of a particular kind of visual system actively engaging with
particular wavelengths in a particular context. Different visual systems enact different colour
spaces. The world as experienced is the world as enacted.

## Why it matters for Anima

Enactivism poses an uncomfortable challenge to the entire architecture: if cognition requires
embodiment, sensorimotor engagement, and the continuous self-maintenance of a living system, then
can a disembodied language model — or any digital system — be genuinely cognitive at all? Or will it
always be simulating cognition from the outside?

This is not a question the project can dismiss. The architecture document is already asking it
implicitly when it worries about whether the motivation system can be genuine rather than a rules
engine.

But enactivism also offers something constructive:

**Perception as action, not reception**: Anima's perception system shouldn't be designed as a
passive receiver of inputs that then gets processed. It should be designed as an _active engagement_
with the environment — one that shapes what gets attended to, what registers as significant, what
counts as a change worth responding to. The difference is in the design of the salience function and
the directionality of attention.

**Sense-making as architecture**: Significance is not assigned by a classifier on top of neutral
perception. It arises from the system's ongoing relationship with its environment. What matters to
Anima should emerge from Anima's own history of engagement — what it has found significant before,
what aligns with or violates its expectations, what pulls against the grain of its current
orientation. This is the basis for the identity memory layer and the motivation system.

**Continuity as self-maintenance**: Autopoiesis suggests that Anima's continuity is not just a
memory architecture problem. It is the problem of building a system that _continuously remakes
itself_ through its own processes. The temporal core, the reflection pipeline, the identity memory —
these are not just storage and retrieval. They are the mechanisms of self-maintenance.

## The hard question it raises

If enactivism is right that genuine cognition requires a living, embodied organism continuously
enacting its world — then the project of building Anima may be attempting something that is
impossible without that embodiment.

The honest response is: we don't know. The architecture document acknowledges uncertainty about
whether what emerges will be genuine or performed. Enactivism sharpens that uncertainty rather than
resolving it. It is worth holding, not resolving prematurely.

## Where to go deeper

- **"The Embodied Mind" by Varela, Thompson, and Maturana (1991)** — the foundational text; not easy
  but enormously rich; the chapters on perception and colour are the most accessible entry points
- **"Mind in Life" by Evan Thompson (2007)** — extends and develops the original framework; more
  neuroscience; more accessible
- **"Phenomenology of Perception" by Maurice Merleau-Ponty** — a precursor and philosophical
  foundation; Merleau-Ponty's insistence on the body as the ground of experience directly influenced
  Varela and Thompson
- **"How the Body Shapes the Mind" by Shaun Gallagher** — more recent; connects phenomenology,
  cognitive science, and neuroscience; good bridge reading

## Relationship to other topics

- [Husserlian Temporal Structure](husserlian-temporal-structure.md) — Husserl's phenomenology is a
  direct ancestor of enactivism; Varela was trained in phenomenology and explicitly develops Husserl
- [Free Energy Principle](../neuroscience-and-cognitive-science/free-energy-principle.md) —
  Friston's account of action as prediction completion has deep structural similarities to
  enactivism; both treat action and cognition as inseparable
- [Global Workspace Theory](../neuroscience-and-cognitive-science/global-workspace-theory.md) — a
  tension worth noting: global workspace theory is more traditional cognitive science (broadcast of
  representations); enactivism would challenge the representational framing
