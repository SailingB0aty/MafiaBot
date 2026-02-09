# MafiaBot (Discord)

A Python Discord bot that runs a game of Mafia in a server: players join, roles are assigned (Mafia / Doctor / Sheriff / Bread Man / Civilians), actions happen in DMs, then the group votes in the main channel. Includes voice-channel audio + silly narrated “story” between rounds.

> Legacy project: this was built years ago and may need a little modernisation to run with current Discord APIs. This repo is here as a demonstration of coding ability.

---

## Features

- In-server Mafia game loop (join → start → DM actions → narrated results → discussion → vote)   
- Roles:
  - **Mafia** chooses someone to kill (DM)
  - **Doctor** chooses someone to save (DM)
  - **Sheriff** accuses someone (DM)
  - **Bread Man** gives bread (DM) :contentReference[oaicite:2]{index=2}
- “Population report” embed showing who is alive/dead
- Voice channel audio cues + story narration using text-to-speech (gTTS + ffmpeg) 

---

## How to play (in Discord)

1. Join a voice channel
2. In a text channel, run:
   - `>mafia`
3. Players type **Join** in that channel
4. When you have **5+ players**, type **Start**
5. Role actions happen via DMs
6. During voting, cast your vote by **mentioning** a player in the main channel

