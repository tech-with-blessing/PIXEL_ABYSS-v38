# PIXEL ABYSS — Agent System

This project has 5 specialist agents. They live in `.agents/` and save
all reports to `.agents/reports/` with timestamps.

## Available Agents

| Agent | File | Trigger |
|---|---|---|
| UI/UX | `.agents/uiux-agent.md` | "run uiux agent" |
| Level Designer | `.agents/level-agent.md` | "run level agent" |
| Performance | `.agents/performance-agent.md` | "run performance agent" |
| Feature Suggester | `.agents/features-agent.md` | "run features agent" |
| Code Reviewer | `.agents/reviewer-agent.md` | "run reviewer agent" |
| Programmer | `.agents/programmer-agent.md` | "run programmer agent" |
| Image Generator | `.agents/image-agent.md` | "run image agent" |

## How to Run an Agent
Read the relevant agent file from `.agents/`, execute the instructions,
then save the report to `.agents/reports/` with this filename format:
`[agent-name]-report-YYYY-MM-DD_HH-MM.md`

Every report must start with:
```
# [Agent Name] Report
Generated: [full timestamp]
PIXEL ABYSS — [version if detectable]
---
```