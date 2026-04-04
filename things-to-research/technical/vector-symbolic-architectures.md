# Vector Symbolic Architectures

## The problem they solve

Cognitive scientists call it the **binding problem**: how does the brain combine separate pieces of
information into coherent representations without confusing them?

If you read "the dog chased the cat", your brain must bind _dog_ to the _chaser_ role and _cat_ to
the _chased_ role — and do this in a way that doesn't confuse the two. It must also represent the
whole sentence as a unit, distinct from "the cat chased the dog" (same components, different
binding).

Classical symbolic AI solves this with pointers and data structures: a node labelled "chase" with
links to "dog" (subject) and "cat" (object). Clean, interpretable, brittle. It breaks under noise
and doesn't generalise gracefully.

Neural networks learn representations but are generally not compositional in a principled way. You
can't take the learned representation of "dog" and the learned representation of "chaser" and
reliably derive "dog as chaser" from them.

**Vector Symbolic Architectures (VSAs)** are a family of formalisms that try to solve this using
high-dimensional vectors and algebraic operations. They sit in the middle: sub-symbolic in their
implementation (it's all vectors and math), but symbolic in their behaviour (you can encode and
recover structured relationships).

## The key operations

VSAs represent all concepts as high-dimensional vectors — typically 1,000 to 10,000 dimensions,
either real-valued, binary, or complex-valued depending on the variant.

**Bundling** (often +, OR, or majority): Combining items into a set or mixture.

```
pet ≈ dog + cat + hamster
```

The result is similar to each component but identical to none. You can query: "is dog part of this
bundle?" and get a high similarity. This represents a set or a superposition.

**Binding** (often ⊗, XOR, or circular convolution): Creating an association between two items.

```
chaser_role ⊗ dog  →  dog_as_chaser
```

The result is _dissimilar_ to both dog and chaser_role individually. It is a new, unique
representation. Critically, binding is reversible:

```
dog_as_chaser ⊗ chaser_role  →  dog  (approximately)
```

**Unbinding**: Recovering one element from a binding given the other. This lets you query: "what was
in the chaser role?" by providing the binding and the role.

A full sentence encoding might look like:

```
sentence = (chaser_role ⊗ dog) + (chased_role ⊗ cat) + (action ⊗ chase)
```

From this bundle, you can ask "what was the chaser?" and approximately recover "dog". This works
even with noise — even if the vector is corrupted, the answer is still approximately correct.

## The main variants

**Holographic Reduced Representations (HRRs)** — Tony Plate, 1995. Uses circular convolution for
binding and addition for bundling. Real-valued vectors. The mathematical properties are
well-studied. "Holographic" because information is distributed across the whole vector rather than
localised.

**Binary Spatter Codes (BSCs)** — Pentti Kanerva. Binary vectors. Binding is XOR, bundling is
majority vote. Extremely efficient — all operations are bitwise. Connects directly to Sparse
Distributed Memory.

**Multiply-Add-Permute (MAP)** — various authors. Uses multiplication (Hadamard product) for
binding. Simpler than circular convolution.

**Fractional Power Encoding** — more recent work. Allows continuous values to be encoded by raising
a base vector to a fractional power. Useful for encoding positions, magnitudes, sequences.

## Resonator Networks

A more recent development (Frady, Kleyko, Sommer — 2020) that solves the _factorization problem_:
given a bundled, bound representation, how do you efficiently recover the constituent factors?

Standard unbinding works when you know one factor and want the other. But often you have a mixed
bundle and want to decompose it completely — you know what the sentence-as-a-whole looks like, and
you want to recover subject, verb, and object simultaneously.

Resonator Networks are a recurrent neural circuit that solves this through iteration. Starting from
random initial guesses, the network resonates toward the correct factorization. It converges quickly
when the capacity of the VSA (number of stored items) is not exceeded.

This is relevant to Anima because memory retrieval from a bundle is exactly this problem: you have a
query (partial or fuzzy) and you want to recover the structured components of what was stored.

## Why it matters for Anima

The insights document proposed VSAs as a candidate for Anima's internal representation language —
the medium in which specialist systems communicate, and in which memory is stored.

The alternative is text: everything rendered as natural language, with the LLM processing it. Text
has the advantage of being the LLM's native medium. But it is sequential, lossy for non-linguistic
content, and requires a language generation step every time something is expressed internally.

VSA vectors could represent events in a form that preserves compositional structure — who did what,
to what, in what context — in a single vector that can be efficiently stored, retrieved by
similarity, bound to other representations, and unbundled to recover components. The LLM would then
be involved at the stage of _interpretation_ and _expression_, not at the stage of internal
representation.

Whether this is the right choice for Anima is genuinely open. But the option is worth understanding.

## Where to go deeper

- **Tony Plate, "Holographic Reduced Representations" (1995)** — the original HRR paper; IEEE TNNLS
- **Kanerva's "Hyperdimensional Computing: An Introduction to Computing in Distributed
  Representation with High-Dimensional Random Vectors" (2009)** — accessible survey; Cognitive
  Computation journal
- **Frady, Kleyko, Sommer, "A Theory of Sequence Indexing and Working Memory in Recurrent Neural
  Networks" (2018)** — connects VSAs to temporal sequences
- **"Vector Symbolic Architectures as a Computing Framework for Nanoscale Hardware" (2021)** —
  survey paper with a good introduction to the field

## Relationship to other topics

- [Sparse Distributed Memory](sparse-distributed-memory.md) — Kanerva's BSCs are a VSA variant; the
  fields are converging under the label "Hyperdimensional Computing"
- [Gärdenfors' Conceptual Spaces](../philosophy/gardenfors-conceptual-spaces.md) — a different
  approach to the same problem (non-linguistic meaning representation); the two could be combined
