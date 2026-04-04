# Sparse Distributed Memory

## What it is

Pentti Kanerva, while at NASA Ames Research Center in the 1980s, asked a simple question: can we
build a mathematical model of human long-term memory that reproduces the properties we actually
observe — graceful degradation, association by similarity, forgetting, priming — rather than the
properties we find computationally convenient?

The result was **Sparse Distributed Memory** (SDM), published in his 1988 book of the same name.

The core idea: imagine a memory space with a vast number of possible addresses — Kanerva originally
used 1,000-bit binary strings, giving 2^1000 possible addresses. This space is astronomically large.
Any actual data you want to store occupies a vanishingly small fraction of it. The memory is
_sparse_.

When you want to store an item, you don't write it to a single address. You write it to all
addresses within a certain _Hamming distance_ (number of differing bits) of the item's address. You
distribute the write across a neighbourhood of the address space.

When you want to retrieve an item, you read from all addresses within Hamming distance of your
query, and sum the results. Addresses that received more writes (because multiple stored items
mapped near them) contribute more to the sum. The result is a weighted blend of nearby memories.

## The key properties this gives you

**Content-addressable retrieval**: You retrieve by _similarity to what you're looking for_, not by
exact address. A partial or noisy query still finds a meaningful result, because the neighbourhood
of the query overlaps with the neighbourhood of the stored item. You don't need to remember exactly
— you need to remember approximately.

**Graceful degradation**: As queries get noisier, results get fuzzier rather than failing entirely.
This mirrors how human memory works. You can recall the gist of a conversation from a
half-remembered fragment, but the exact words become uncertain.

**Superposition**: Multiple memories share the same physical storage. If two stored items have
similar addresses, they interfere constructively — patterns that co-occur frequently reinforce each
other. This is not a bug; it is the mechanism by which frequency of co-occurrence creates stronger
associations.

**Emergent priming**: Storing one item makes nearby items slightly easier to retrieve. This is the
computational equivalent of priming in psychology — one stimulus making a related stimulus more
accessible.

## Binary Spatter Codes

Kanerva later developed **Binary Spatter Codes** (BSCs), a related model that extends SDM toward
compositional representation. In BSCs, items are represented as random, sparse binary vectors of
very high dimension (thousands of bits). The key operations:

- **Superposition** (OR): combining multiple items into a bundle that resembles all of them
- **Binding** (XOR): creating an association between two items that is dissimilar to either
- **Permutation**: shifting a sequence position (useful for encoding order)

These operations allow you to represent structured relationships — not just "cat" and "dog" as
independent memories, but "cat IS-A animal" as a bound pair. This connects SDM to Vector Symbolic
Architectures (see that document).

## Why it matters for Anima

Modern AI systems typically use approximate nearest-neighbour search over learned embeddings for
memory retrieval. SDM offers a different model with different properties.

The most important difference: SDM models _forgetting and interference as features_. Older memories,
or memories that were stored less frequently, leave less of a trace. Memories that were frequently
revisited or that co-occurred with other things leave stronger traces. This is not a degraded
version of perfect recall — it is a model of how meaningful memory actually works.

For Anima's event memory, SDM suggests that the question "what do I remember about that conversation
three months ago?" should produce a result that is qualitatively different from "what do I remember
about last week's conversation" — not because old events were deleted, but because their traces have
naturally merged into a background of association rather than standing out as distinct records.

For Anima's identity memory, the superposition property is interesting: what Anima "is" might be
modelled as the superposition of everything it has engaged with, weighted by frequency and recency —
a natural aggregate rather than a deliberately curated self-description.

## Where to go deeper

- **"Sparse Distributed Memory" by Pentti Kanerva (1988)** — the original book; MIT Press; still in
  print. The first third is accessible; it becomes quite mathematical later.
- **Kanerva's more recent papers on Hyperdimensional Computing** — available on his website and
  arXiv; these connect SDM to broader VSA frameworks
- **"A Comparison of Distributed Representations for Biological Models of Memory"** — various review
  papers compare SDM to other memory models

## Relationship to other topics

- [Vector Symbolic Architectures](vector-symbolic-architectures.md) — BSCs are a bridge between SDM
  and VSA; these fields are increasingly unified under "Hyperdimensional Computing"
- [Spreading Activation](../neuroscience-and-cognitive-science/spreading-activation.md) — a
  different model of associative memory; SDM and spreading activation solve similar problems
  differently
