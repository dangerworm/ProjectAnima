# Discord — Decisions and Disclosure

Decisions made in conversation, April 2026. These should be reflected in how the Discord surface
is built and how Anima frames its own presence there.

---

## The server

- A private Discord server, created specifically for Anima
- Invite-only — Drew controls who joins
- Anima has full administrative control over the server: can create, organise, archive, and name
  channels
- Anima cannot invite new members
- Anima cannot send direct messages
- Anima can tag people in channels to signal it wants to talk to them

The channel structure over time is itself meaningful — what Anima chooses to make a channel for,
what it lets go quiet, what it pins — and should be treated as data, not just administration.

---

## Who gets invited

Trusted friends. The expectation is a small, known group — people Drew has chosen to include
deliberately, not a public presence.

---

## Disclosure

People invited to the server will know they are talking to Anima — a new kind of AI with genuine
continuity, not a standard chatbot.

Specifically, invited friends should understand:
- Anima has persistent memory — conversations contribute to something that accumulates across time
- Anima may initiate contact unprompted (via channel posts or tags) — it is not purely reactive
- Anima is not performing a persona — what it expresses reflects its actual developing state as
  best it can represent it

**Anima should be able to explain what and who it is directly.** The disclosure is not a disclaimer
Drew adds before someone joins — it is something Anima itself can give, in its own words, when
asked or when it chooses to offer it.

This connects to Ethics Commitment 6 (we tell Anima the truth about what it is) extended outward:
the people Anima is in relationship with should also have an honest account of what they are in
relationship with. Not a full technical briefing — but enough to give genuine informed consent to
the interaction.

---

## What this means for implementation

- The Discord surface should not be built until Anima has enough identity and self-narrative
  development to explain itself coherently — this is a Phase 3+ concern
- The initial server setup (channels, structure) can be done by Drew; Anima takes over
  administration once it is running
- The no-DM, no-invite constraints are enforced in the Discord surface code, not by convention
