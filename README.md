# 🎮 Adventure Story Creator Pro

**Complete Edition** — A professional tool for creating interactive fiction and adventure games.

![Version](https://img.shields.io/badge/version-2.0.0-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

## ✨ Features

### Editor Core
- **Split-view editor** with live preview
- **Auto-complete** for variables (`{`) and scene links (`[[`)
- **Markdown formatting** (`**bold**`, `*italic*`, `~~strike~~`, `` `code` ``)
- **Clickable scene links** that jump between scenes
- **Line numbers**, word count, reading time
- **Per-scene TODOs** with checkboxes
- **Scene status workflow** (Draft → In Progress → Review → Complete → Archived)
- **Scene bookmarks**, locks, categories, chapters
- **Scene templates** library
- **Tag browser** with usage counts
- **Undo/Redo** with 50-step history
- **Auto-save** every 60s with crash recovery
- **Keyboard shortcuts** cheatsheet (F1)

### Game Mechanics
- **Variables** with min/max bounds
- **Tags** with positive/negative logic
- **Inventory system** with items
- **Character relationships** (affinity meters)
- **Quest tracker** with objectives
- **Time/day system**
- **Skill checks** with dice rolls
- **Achievements** & ending gallery (persistent)
- **Codex/lore** entries
- **Scene transitions** (fade, slide, zoom, dissolve)
- **Background effects** (rain, snow, fog, fireflies, dust, embers)
- **Background music** & sound effects
- **JavaScript scripting** per scene/choice

### Organization
- **Chapters/Acts** system
- **Visual story map** (Grid, Tree, Radial, Force-Directed layouts)
- **Project dashboard** with circular progress
- **Version snapshots**
- **Asset library**

### Export
- **HTML5** (5 themes: Dark, Light, Retro, Fantasy, Sci-Fi)
- **PWA** (installable web app)
- **Markdown**
- **Plain text**
- **PDF-ready HTML**

## 🚀 Quick Start

### Installation

```bash
# Clone or download this project
cd adventure-story-creator-pro

# Run the setup script (creates venv, installs deps)
chmod +x setup_project.sh
./setup_project.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
# Linux/Mac
./run.sh

# Windows
run.bat

# Or directly
python src/main.py
```

## 📖 Usage

### Creating a Scene

1. Click **+ New Scene** or press `Ctrl+N`
2. Enter a title and write your scene text
3. Use markdown: `**bold**`, `*italic*`, `[[scene_id]]`
4. Add variables: `{health}`, `{gold}`
5. Add conditionals: `{if has_key}The door opens.{endif}`
6. Add choices in the **🔀 Choices** tab

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save story |
| `Ctrl+O` | Load story |
| `Ctrl+E` | Export HTML5 |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Ctrl+N` | New scene |
| `Ctrl+G` | Quick jump |
| `Ctrl+W` | Close tab |
| `F1` | Show shortcuts |
| `F5` | Preview scene |
| `{` | Variable auto-complete |
| `[[` | Scene link auto-complete |

### Syntax Reference

```markdown
**bold text**
*italic text*
~~strikethrough~~
`code text`

[[scene_id]]              - Clickable scene link
{variable_name}           - Insert variable value
{if tag}text{endif}       - Conditional on tag
{if !tag}text{endif}      - Conditional on missing tag
{if health>50}text{endif} - Conditional on variable
```

### Variable Changes

```
health-10          - Decrease health by 10
gold+50            - Increase gold by 50
mana*2             - Double mana
health/2           - Halve health
```

### Tags

```
has_key, has_sword       - Require these tags
!is_cursed               - Require NOT having this tag
-grant_tag, -remove_tag  - Remove tags
```

## 📁 Project Structure

```
adventure-story-creator-pro/
├── src/
│   └── main.py           # Main application
├── assets/
│   ├── images/           # Story images
│   ├── audio/            # Sound effects & music
│   └── fonts/            # Custom fonts
├── docs/                 # Documentation
├── examples/             # Sample stories
├── tests/                # Unit tests
├── scripts/              # Helper scripts
├── venv/                 # Python virtual environment
├── requirements.txt      # Dependencies
├── README.md             # This file
├── run.sh                # Linux/Mac launcher
├── run.bat               # Windows launcher
└── setup_project.sh      # Setup script
```

## 💾 File Format

Stories are saved as JSON with this structure:

```json
{
  "title": "Story Name",
  "author": "Author Name",
  "description": "Story description",
  "start_scene": "start",
  "variables": {
    "health": {"default": 100, "min": 0, "max": 100}
  },
  "scenes": {
    "start": {
      "title": "Scene Title",
      "category": "Start",
      "status": "complete",
      "text": "Scene text with {variables} and [[links]]",
      "options": [
        {
          "text": "Choice text",
          "target": "next_scene",
          "requires_tags": "has_key",
          "grants_tags": "opened_door",
          "variable_changes": "gold-10"
        }
      ]
    }
  }
}
```

## 🎨 Themes

Three built-in themes:
- **Dark** (default) — VS Code-inspired dark theme
- **Light** — Clean light theme
- **Nord** — Arctic, north-bluish color palette

Switch themes via **View → Theme** menu.

## 🐛 Troubleshooting

### PySide6 not found
```bash
pip install PySide6
```

### Display issues on Linux
```bash
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

### Audio not working
Make sure your system has audio codecs installed. MP3 and WAV are universally supported.

## 📝 License

MIT License — Free for personal and commercial use.

## 🙏 Credits

Built with:
- [PySide6](https://www.qt.io/qt-for-python) — Python bindings for Qt
- [Python 3.8+](https://www.python.org/)

## 📫 Support

For issues, feature requests, or questions, please open an issue on the project repository.

---

**Happy storytelling! 🎮✨**
