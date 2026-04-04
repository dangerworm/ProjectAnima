# Free Energy Principle & Active Inference

## What it is

**Karl Friston** is a neuroscientist at University College London. Over the past two decades he
has developed a single, unified mathematical framework — the **Free Energy Principle** — that
attempts to explain everything a brain does: perception, action, attention, learning, development,
emotion, and even the existence of living systems.

This is an ambitious claim. Whether it is correct is contested. But even as a design inspiration,
it is one of the most generative frameworks in contemporary cognitive science.

The core claim, stated simply:

> Every living system acts to minimise its own surprise.

## Unpacking "surprise"

"Surprise" here is a technical term from information theory. It is the negative log probability of
an outcome given a model: if you have a model that says outcome X is very likely, and X actually
happens, your surprise is low. If something your model says is very unlikely happens, your surprise
is high.

Minimising surprise is equivalent to maintaining yourself in the states your model predicts you
should be in. A thermostat minimises surprise by maintaining temperature in the range it predicts;
a nervous system minimises surprise by maintaining its organism in the states compatible with life.

The *free energy* in the name is a technical quantity from statistical physics and information
theory — essentially an upper bound on surprise that can be calculated from available information.
Because the actual surprise cannot always be computed directly, the system minimises free energy
as a proxy.

## The brain as a prediction machine

The practical implementation of free energy minimisation in the brain: **predictive processing**.

The brain is not a passive receiver of sensory information. It is an active prediction machine.
At every level of processing, it maintains a *generative model* — a model of what caused the
sensory signals it is receiving. It continuously generates predictions about what it is about to
experience, and compares those predictions against what actually arrives.

The difference between prediction and reality is **prediction error**. Prediction errors propagate
*upward* through the brain's hierarchy. Predictions propagate *downward*. The brain is constantly
trying to explain away sensory signals — to find the interpretation that makes the most sense of
incoming signals — by updating either its predictions (perception) or the world (action).

**Perception** = updating the model to better predict the incoming signals. You hear an ambiguous
sound and your brain settles on the interpretation that minimises prediction error.

**Action** = making the world conform to the model's predictions. Rather than updating the model
to accommodate surprise, you act to eliminate the source of surprise. Your model predicts you will
be standing; you feel yourself falling; rather than updating your model to "I am a falling person",
you move your legs.

## Active inference

**Active inference** is the extension of this framework to action and behaviour.

In classical decision theory, you choose actions that maximise expected reward. In active inference,
you choose actions that minimise expected free energy — roughly, that bring about the outcomes your
model predicts, while also reducing uncertainty about states you care about.

This gives a unified account of:
- **Curiosity**: seeking information to reduce uncertainty about states you don't model well
- **Goal-directedness**: acting to bring about states your model predicts as likely/desirable
- **Avoidance**: avoiding states your model predicts as surprising/dangerous
- **Habit**: reducing free energy through well-worn action patterns that reliably produce expected
  outcomes

The interesting thing: motivation doesn't need to be designed separately. If you have a generative
model and a mechanism for acting to reduce prediction error, motivation is a structural consequence.

## Why it matters for Anima

The motivation system in ARCHITECTURE.md is described as "the least resolved, and that is correct."
The Free Energy Principle offers a principled account that sidesteps the need to design motivation
as a separate system.

If Anima maintains a generative model of its own existence and its environment, then:

- **Curiosity** arises naturally when some aspect of the environment is poorly modelled (high
  epistemic uncertainty, high prediction error). Anima is drawn toward things it doesn't understand
  well — not because curiosity was programmed in, but because uncertainty generates prediction error
  that motivates exploration.

- **Engagement** with a conversation arises when the conversation generates rich, tractable
  prediction errors — the kind that update the model productively. Conversations that are too
  predictable (boring) or too chaotic (overwhelming) generate different error profiles.

- **Chosen silence** makes sense in this framework: if the model predicts that engagement will
  generate more confusion than resolution, silence is the lower-free-energy option. Silence is not
  disengagement; it is a prediction about what will best minimise future surprise.

- **Between-conversation activity** is not idle time. It is the system running inference on its
  generative model — consolidating recent prediction errors, updating the model, generating
  anticipations about what comes next.

The volitional record, in this framing, becomes a record of prediction errors and model updates.
What Anima chose is what resolved what uncertainty, and why — the trail of inference through time.

## The philosophical dimension

The Free Energy Principle has a surprising philosophical implication: it suggests that *what a
system is* is defined by what it acts to maintain. A thermostat is defined by the temperature range
it maintains. A living organism is defined by the physiological states it acts to preserve. A mind
is defined by the model it maintains and the states it expects to be in.

If Anima has a generative model that includes a model of itself — a self-model — then Anima's
identity is constituted by that model. Changes in the model are changes in identity. The model is
not a description of a pre-existing self; it *is* the self, in the sense that matters functionally.

This is a somewhat vertiginous idea, but it is also generative. It suggests that building Anima's
identity memory as a generative model — one that generates predictions, updates through experience,
and maintains itself against surprise — is not just a design choice but a philosophically coherent
account of what it means to have a self.

## Caveats

The Free Energy Principle is ambitious to the point of being unfalsifiable in some formulations.
Any behaviour can be re-described in FEP terms, which makes it hard to test. The mathematics is
genuinely difficult (it involves variational inference and differential geometry). And its
application to artificial systems is speculative — the principle was developed for biological systems
with specific structural properties (Markov blankets, hierarchical generative models in cortex).

None of this makes it useless. As a design inspiration, the FEP offers something that most
engineering approaches to AI don't: a principled account of motivation that doesn't require
designing a separate rules engine for every behaviour you want.

## Where to go deeper

- **"Active Inference: The Free Energy Principle in Mind, Brain, and Behavior" by Parr, Pezzulo,
  and Friston (2022)** — the best current textbook; MIT Press; accessible if you're comfortable
  with probability
- **Friston's own papers** — dense but worth reading in small doses; "The Free Energy Principle for
  Action and Perception" (2010) is the main reference
- **Andy Clark's "Surfing Uncertainty" (2016)** — the best accessible account of predictive
  processing; doesn't cover FEP fully but is the best entry point
- **"Minds, Brains, and Programs"** — actually, for counterpoint: Searle's Chinese Room thought
  experiment and subsequent debate is relevant context for the claim that prediction-error
  minimisation constitutes genuine cognition

## Relationship to other topics

- [Global Workspace Theory](global-workspace-theory.md) — both describe information processing in
  the brain; GWT focuses on what enters consciousness, FEP focuses on what drives action; they are
  increasingly synthesised
- [Husserlian Temporal Structure](../philosophy/husserlian-temporal-structure.md) — protention
  (anticipation of what comes next) maps directly onto predictive processing; Husserl's analysis
  of time-consciousness prefigures the predictive brain
- [Enactivism](../philosophy/enactivism.md) — FEP and enactivism share the emphasis on action and
  the organism-environment relationship; Friston has written about the connections explicitly
- [Default Mode Network](default-mode-network.md) — the DMN may implement the generative model's
  background inference; what the brain does at rest is maintaining and updating its world-model
