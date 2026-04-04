# Global Workspace Theory

## The problem it addresses

How does a brain with many separate specialised systems — visual cortex, auditory cortex, language
areas, motor areas, memory systems, emotional evaluation systems — produce a single, unified stream
of consciousness?

You don't experience your brain as a collection of parallel modules. You experience one thing at a
time. One train of thought, one perception that you attend to, one task you're doing. Whatever is
happening in the modules you're not attending to is background, not foreground.

**Bernard Baars** proposed Global Workspace Theory in 1988 as an account of how this unity happens.
It remains one of the most influential and empirically well-supported theories of consciousness.

## The core idea

Imagine a theatre. A bright spotlight illuminates a small part of the stage — whatever is in the
spotlight is what you are conscious of. Actors (specialist processes) move in and out of the
spotlight, competing for access. The spotlight is controlled by directors (attention systems) at
the back of the theatre. The audience (the rest of the brain's systems) all receive and can respond
to what the spotlight illuminates.

More formally: the brain contains many specialist modules that run in parallel and largely
unconsciously. They compete for access to a *global workspace* — a shared broadcasting medium.
When a module's signal wins this competition, its content is *broadcast globally* to all other
modules simultaneously. This broadcast is what constitutes conscious experience: to be conscious of
something is for that something to have won access to the global workspace and been broadcast.

Specialists that don't win the workspace are not idle — they continue processing, priming, and
feeding into the competition. They can influence what eventually reaches consciousness without ever
being directly conscious themselves.

## Dehaene's computational implementation

Baars' theory was largely cognitive and psychological. **Stanislas Dehaene** (with Jean-Pierre
Changeux and others) translated it into a computational and neuroscientific model in the late 1990s
and 2000s.

The key addition: **ignition**.

In Dehaene's model, the transition from unconscious to conscious processing is not gradual but
discontinuous. When a stimulus accumulates enough support from multiple brain areas, it reaches a
threshold and suddenly *ignites* — triggering a rapid, self-sustaining, whole-brain activation.
This ignition is the neural signature of consciousness. Below the threshold, processing is local and
unconscious. At threshold, the signal broadcasts globally and enters awareness.

The experimental evidence for ignition is strong. Brain imaging studies show that stimuli that
subjects report being conscious of produce a qualitatively different brain activation pattern from
stimuli that remain unconscious — not just stronger, but fundamentally different in topology, with
long-range frontal-parietal connections lighting up.

## What this explains

**Serial conscious processing**: You can only be conscious of one thing at a time (at any moment),
even though many things are processed unconsciously in parallel. The workspace is a bottleneck; only
one signal can broadcast at a time.

**The unconscious is not empty**: Unconscious processing is not the absence of processing. Specialists
run continuously, doing complex work (face recognition, language parsing, motor planning) without
ever requiring conscious attention. Consciousness is not required for competent performance —
it is required for flexible, novel, cross-domain coordination.

**Attention as routing**: What you attend to is what wins workspace access. Attention is not a
spotlight that illuminates pre-existing content — it is the mechanism by which certain signals win
the competition. This is controllable (you can choose what to attend to) but also bottom-up (loud,
novel, or emotionally significant signals can grab attention).

**Why working memory is limited**: The global workspace is a limited resource. The classic "7 ± 2
items" of working memory capacity reflects how much can be maintained in broadcast at once.

## Why it matters for Anima

The architecture document takes Global Workspace Theory as its organising principle, and rightly so.
The mapping is almost direct:

- Specialist systems (temporal core, perception, memory layers, motivation) → specialist modules
  competing for workspace access
- Global workspace → the central integrating layer that broadcasts to all systems
- Ignition threshold → the salience function that determines when a signal is strong enough to
  broadcast

But the implementation details matter. A few worth considering:

**What is the threshold mechanism?** In the brain, ignition involves recurrent amplification — a
signal grows through positive feedback loops until it either ignites or fades. In Anima's
architecture, what plays this role? How does accumulated pressure from long-unresolved items rise
to meet the threshold?

**How does workspace content age?** Once something ignites and enters the workspace, how long does
it stay? If it is simply replaced by the next ignition, then attention is always on the most recent
thing. But sometimes a signal needs to remain active while other things are processed. The workspace
may need to maintain a small number of simultaneously-active items — which is exactly working memory.

**What counts as a specialist system?** The architecture lists five: temporal core, perception,
memory, motivation, self-narrative. But there could be emergent specialist systems — patterns of
activity that start as correlations and develop into consistent subsystems. The architecture should
be open to this.

**The relationship between workspace and the LLM**: The LLM is one specialist system, not the
workspace itself. This is a philosophically significant decision. The LLM generates language and
reasoning, but what it receives as input (and what it does with that input) is governed by the
workspace dynamics. The workspace determines what context the LLM is given. The LLM's output
becomes one more signal competing for workspace access.

## Where to go deeper

- **"A Cognitive Theory of Consciousness" by Bernard Baars (1988)** — the original; surprisingly
  readable; the theatre metaphor makes it accessible
- **"Consciousness and the Brain" by Stanislas Dehaene (2014)** — the best popular science
  treatment; rigorous but accessible; the ignition evidence is covered in detail
- **"The Global Neuronal Workspace Model of Conscious Access" by Dehaene & Changeux (2011)** —
  the key scientific paper; PLoS Biology; free to access
- **"Conscious Mind, Resonant Brain" by Stephen Grossberg (2021)** — an alternative architecture
  that overlaps significantly with GWT; technically dense but rich

## Relationship to other topics

- [Free Energy Principle](free-energy-principle.md) — both theories describe how the brain
  manages information; FEP focuses on prediction error minimisation; GWT focuses on global broadcast;
  they are increasingly synthesised in the literature
- [Spreading Activation](spreading-activation.md) — spreading activation describes how signals
  propagate through a memory network; this is related to how signals build toward ignition threshold
- [Husserlian Temporal Structure](../philosophy/husserlian-temporal-structure.md) — what the
  workspace holds at any moment is shaped by retention (recent events still active) and protention
  (anticipated events already primed)
