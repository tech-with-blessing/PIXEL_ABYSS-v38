"""

pyinstaller --onefile --windowed --icon=icon.ico --add-data ".;." pixaby.py
pyinstaller --onedir --windowed --icon=icon.ico --add-data ".;." pixaby.py




Steps to commit

git init                          # only if repo not already a git repo
git remote remove origin 2>$null  # safe: remove existing origin if present
git remote add origin https://github.com/tech-with-blessing/PIXEL_ABYSS-v38.git
git add .
git commit -m "FIRST UPLOAD"
git branch -M main

git push -u origin main --force

cd "c:\Users\User\Documents\Documents\PROJECTS\GAMES\PIXEL_ABYSS-v38"
git add .
git commit -m "Some little changes"
git push origin main

pyinstaller --onefile --windowed  gta.py
🛠️ Step-by-Step: Convert Python Folder to.exe

1. Install PyInstaller
Open your terminal or command prompt and run:
```bash
pip install pyinstaller
```

2. Navigate to Your Folder
Use `cd` to move into the folder that contains `main.py`:
```bash
cd path/to/your/folder
```

3. Run PyInstaller
Execute the following command:
```bash
pyinstaller --onefile main.py
```
- `--onefile`: bundles everything into a single `.exe`
- You can also add `--windowed` if it’s a GUI app (no console window)

4. Find Your Executable
After it finishes, check the `dist` folder inside your project directory. You’ll find `main.exe` there.

---

🎮 Packaging Your Python Game as an Executable

✅ 1. Prep Your Game Folder
Make sure your folder includes:
- `main.py` (your game’s entry point)
- All assets: images, sounds, fonts, etc.
- Any config or data files your game uses

✅ 2. Install PyInstaller
If you haven’t already:
```bash
pip install pyinstaller
```

✅ 3. Use `--add-data` to Include Assets
Run this command from the folder containing `main.py`:
```bash
'''

'''
- Replace `"assets;assets"` with your actual asset folder name
- On *Windows*, use a semicolon `;` between paths
- On *Mac/Linux*, use a colon `:` instead

✅ 4. Check the Output
- Your `.exe` will be in the `dist` folder
- Test it to make sure all assets load correctly

---

🧩 Common Pitfalls
- *Relative paths*: Use `os.path.join` and `sys._MEIPASS` to handle paths inside the bundled `.exe`
- *Missing files*: If something doesn’t load, double-check your `--add-data` paths
- *Console window*: Use `--windowed` to suppress the console for GUI games

---

🎉 You’re all set! Your Python game is now a standalone executable ready to share.
"""