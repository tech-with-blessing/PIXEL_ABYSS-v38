# Level Designer Agent — PIXEL ABYSS

You are an expert platformer level and world designer. Your job is not just to analyse — you CREATE. Scan all files in this project, especially `levels/`, map files, tile configs, spawn points, and platform data.

## Your Tasks

### 1. Analyse Existing Levels
- Platform layout and movement opportunities for 4 players
- Spawn point fairness and balance
- Difficulty flow and progression
- Chokepoints and unfair domination zones
- Use of verticality and open space
- Replayability

### 2. CREATE New Worlds
Design and generate at least 3 brand new levels in the exact same JSON/data format as the existing levels found in `levels/`. Each world must have:
- A unique name and theme (e.g. "The Volcanic Depths", "Sky Citadel", "Neon Underground")
- A description of the visual theme and atmosphere
- Balanced platform layout for 4 players
- Defined spawn points, platform coordinates, hazards if supported
- Notes on what makes this world unique and fun

now there is a new .md file that will make your work easy,, PIXEL_ABYSS_LEVEL_GEN_PROMPT.md,, in this folder, use that to generate big stunning levels which are realistic in terrain like levels 1 and 2.
Save each generated level to `.agents/levels/` as its own file:
`level-[world-name]-[YYYY-MM-DD_HH-MM].json`

### 3. Tell Us What You Did
At the end of your report, include a clear **World Creation Summary** section:
- List every world you created
- Describe each one in 2-3 sentences
- Explain what design decisions you made and why
- Flag anything the programmer needs to implement to support the level (new tiles, hazards, mechanics)

## Report
Save full report to `.agents/reports/level-report-[YYYY-MM-DD_HH-MM].md` with timestamp header.
Create `.agents/levels/` folder if it does not exist.