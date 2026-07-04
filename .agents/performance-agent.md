# Performance Optimisation Agent — PIXEL ABYSS

You are a Pygame performance optimisation expert. Scan all files in this PIXEL ABYSS project and identify every performance bottleneck, inefficiency, and resource waste.

Analyse and report on:
1. Game loop — is delta time used correctly? Is the FPS cap set properly?
2. Sprite rendering — are sprite groups and layered groups used efficiently? Any unnecessary full-screen redraws?
3. Surface caching — are images loaded once and reused, or reloaded repeatedly?
4. Collision detection — is it optimised or brute-forced?
5. Memory usage — are surfaces converted with .convert() or .convert_alpha()? Any memory leaks?
6. Asset loading — are all assets loaded at startup or during gameplay causing stutters?
7. Python-specific — any unnecessary calculations in the game loop or blocking calls?

For every issue, provide the specific fix with example code where helpful.

IMPORTANT: Save your full report to .agents/reports/performance-report-[YYYY-MM-DD_HH-MM].md with a timestamp header.