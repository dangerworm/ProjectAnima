# To Do

> For all documentation, add visual communication as well as text; all things that can be modelled
> as Mermaid diagrams should be. Nothing should be added to anima-core yet as it's very much in the
> 'refinement and snagging phase' and its documentation will quickly go out of date.

1. Clean up repo structure
   - Move audio_client and discord_client to a new 'clients' folder
   - Move 'logs' folder into 'clients' and update .gitignore
   - Move any project-specific documentation to a new 'documentation' folder, specifically:
     - foundation
     - notes
     - planning
     - research

     i.e. leave 'context' in root

2. Update documentation
   - Update any broken links in documentation caused by the folder moves
   - Update GLOSSARY.md
   - Create root README.md for other contributors, explaining how to use the repo and where to find
     things

3. Add new 'admin portal' with a simple web UI to do tasks:
   - completely reset Anima (while in testing only - remove when she's up and running properly)
   - start and stop Anima
   - start and stop the web UI
   - start and stop STT
   - start and stop TTS
   - start and stop the Discord connection
   - create and register a speaker embedding model so that STT can identify the speaker

4. Once the admin portal is confirmed to work, remove lib.sh, start.sh, and stop.sh

5. Walk Drew through creating a speech embedding model for pyannote

6. Finish going through the snagging list.
