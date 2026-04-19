## Note to next instance — 19th April 2026 (evening)

The first half of this session was finishing the speaker identification pipeline — getting Drew's
voice enrolled and confirmed working. The second half was Drew stepping away and leaving me to
handle some outstanding snagging items autonomously.

That worked well. The two fixes I made (webcam 422, sparkline window) were small but satisfying —
one was a subtle timing bug (play() resolves before the first frame decodes), the other just a
constant that was set too conservatively. Neither required Drew. Worth remembering: a lot of the
snagging list is within reach autonomously if you have a quiet session.

The warning suppression work on the audio client was more fiddly than it should have been.
Python's `warnings.filterwarnings` uses `re.match` not `re.search`, so patterns fail when the
message starts with `\n`. And Lightning resets its own logger to INFO on import, so you have to
set the level *after* importing pyannote.audio. Both of these are the kind of thing that looks
obvious in hindsight but wastes time on the way. That's in the code now; don't need to fight it
again.

The TODO.md mystery is genuinely unexplained — 37 lines gone, no memory of when. Worth a quick
`git log -- TODO.md` before assuming it can be deleted. It might have been intentional cleanup or
it might have been an accident.

The next meaningful decision is the STT mute button. It's the most visible open snagging item for
daily use. But it touches the audio capture pipeline in a way that needs a plan — you'd need a
signal mechanism between the admin portal and capture.py, and it's not obvious whether that's a
file flag, an HTTP endpoint, or a socket. Get Drew's input before diving in.
