# Gärdenfors' Conceptual Spaces

## The problem it addresses

There is a longstanding tension in theories of mind between two approaches to representing meaning:

**Symbolic AI** represents knowledge as discrete symbols and logical relations. `dog(rex)`,
`is-a(dog, animal)`, `has(dog, four-legs)`. Clean, explicit, composable, brittle. It struggles with
graded judgments (is a hot dog a sandwich?), with learning from examples, and with the fact that
human concepts have fuzzy edges rather than crisp definitions.

**Sub-symbolic AI** (neural networks, embeddings) learns continuous representations from data. It
handles fuzziness naturally and generalises from examples. But the representations are opaque — you
can't inspect a neural network's embedding of "dog" and understand what it represents. And it is not
obviously compositional: you can't reliably derive the representation of "large dog" by combining
the representations of "large" and "dog".

**Peter Gärdenfors** proposed Conceptual Spaces in his 2000 book as a _middle level_ between these
two: continuous like sub-symbolic representations, but with geometric structure that is
interpretable.

## The core idea

A conceptual space is a multi-dimensional geometric space where:

- Each **dimension** corresponds to a perceptual or conceptual quality (brightness, size, weight,
  temperature, shape, valence...)
- Dimensions are organised into **domains**: the colour domain (hue × saturation × brightness), the
  size domain (length × width × height), the emotional domain (valence × arousal), and so on
- **Concepts** are _convex regions_ in this space — a region is convex if, for any two points in it,
  the straight line between them is also in the region
- **Instances** are points
- **Similarity** is _distance_ — two things are more similar if their points are closer

The convexity requirement is not arbitrary. It captures a natural property of concepts: if a tomato
and a watermelon are both fruit, then anything "between" them (similar to both in the relevant ways)
is also likely to be fruit. Concepts don't have arbitrary holes.

## What this explains that symbols don't

**Graded membership**: Is a penguin a typical bird? In a symbolic system, either penguin is a bird
or it isn't. In conceptual space, the penguin point is far from the prototypical bird point (at the
centre of the bird region), so it is a bird but not a typical one. Graded membership is distance
from prototype.

**Typicality**: The _prototype_ of a concept is the centroid of the region. Robins are typical
birds; penguins are not. This matches how humans actually use concepts.

**Similarity without identity**: Two things can be similar without being the same category. Their
points are close in the space even if no category boundary places them together.

**Cross-domain properties**: Colour terms like "warm" (which applies to both temperature and colour)
work because warmth in the temperature domain and warmth in the colour domain map onto similar
positions in a shared affective dimension. The geometry reveals why metaphors work.

**Natural predicates**: Gärdenfors argues that natural language predicates (adjectives, nouns,
verbs) map onto convex regions in conceptual space. This is why "tall" applies to a coherent range
of heights — because heights form a dimension, and "tall" is the upper region of it.

## Properties and relations

A **property** is a convex region in a single domain. "Blue" is a region in colour space. "Hot" is a
region in temperature space.

A **concept** is a convex region across multiple domains. "Apple" involves colour, shape, taste,
size, and texture — a region in the joint space of all those domains.

**Relations** between concepts are geometric: is-larger-than is a consistent direction in size
space; is-brighter-than is a consistent direction in brightness space. Abstract relations like "more
important than" can be treated similarly if importance has a dimension.

## Why it matters for Anima

The architecture poses the internal representation language as an open question, explicitly
rejecting text as the default. Conceptual Spaces are one principled answer.

If Anima's perception system represents events and inputs as points or regions in a conceptual
space, then:

- **Similarity is natural**: two events are similar if their points are close. No need for a
  similarity function — it's just distance.
- **Conceptual drift is trackable**: if Anima's representation of "interesting" shifts over time
  (what counts as interesting changes as Anima develops), the centroid of the "interesting" region
  moves. This shift is the geometric signature of a change in orientation.
- **Unresolved questions have a shape**: a question that sits at the boundary between two regions —
  "is this situation more X or Y?" — is geometrically a point near a boundary. _Preserved
  strangeness_ might be boundary cases, points that sit near concept edges and haven't resolved into
  a clear region.
- **Identity has a geometry**: Anima's developing self-concept is a region or collection of regions
  in conceptual space. Growth is movement and expansion of those regions.

## Gärdenfors and language

Gärdenfors has extended the theory to cover language acquisition (children learn concepts by
learning where to draw boundaries in conceptual space) and semantics (word meanings are mappings
onto conceptual space). This connects to why language can be a useful _output_ medium even if it is
not the right _internal_ representation — language maps onto conceptual space, and conceptual space
can be rendered in language.

## Where to go deeper

- **"Conceptual Spaces: The Geometry of Thought" by Peter Gärdenfors (2000)** — the primary text;
  MIT Press; accessible to non-philosophers in the first half; the second half gets more technical
- **"The Geometry of Meaning: Semantics Based on Conceptual Spaces" by Gärdenfors (2014)** — a more
  recent and more practical book; covers language and meaning specifically
- **Papers on computational implementations** — there is a growing literature on implementing
  conceptual spaces computationally; search for "conceptual spaces + machine learning"

## Relationship to other topics

- [Vector Symbolic Architectures](../technical/vector-symbolic-architectures.md) — VSAs are another
  approach to the same problem (non-linguistic structured representation); VSAs are more algebraic,
  conceptual spaces are more geometric; they could potentially be combined
- [Husserlian Temporal Structure](husserlian-temporal-structure.md) — Husserl's retention and
  protention could be modelled geometrically: retention is a trajectory through conceptual space,
  protention is an anticipated direction
- [Spreading Activation](../neuroscience-and-cognitive-science/spreading-activation.md) — spreading
  activation on a semantic network is roughly distance-based retrieval on a graph; conceptual spaces
  generalise this to continuous geometry
