#!/usr/bin/env python
"""
Adventure Story Creator Pro — Complete Edition
A professional tool for creating interactive fiction and adventure games.

Features:
- Split-view editor with live preview
- Auto-complete for variables and scene links
- Markdown formatting with clickable scene links
- Tag browser and scene templates
- Scene status workflow (Draft → In Progress → Review → Complete → Archived)
- Per-scene TODOs with checkboxes
- Variables, tags, inventory, quests, relationships
- Achievements, codex, ending gallery (persistent)
- Skill checks with dice rolls
- Time/day system, chapters, visual map
- JavaScript scripting per scene/choice
- Export to HTML5 (5 themes), Markdown, Plain Text
- Auto-save with crash recovery
- Multiple UI themes (Dark, Light, Nord)
"""

import sys, json, uuid, base64, copy, os, re, random, math
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QComboBox, QLabel, QStackedWidget, QFileDialog, QMessageBox, QSplitter,
    QGroupBox, QScrollArea, QTabWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QStatusBar, QSlider,
    QDialog, QFormLayout, QCheckBox, QSpinBox, QMenu, QInputDialog, QGridLayout,
    QProgressBar, QShortcut, QTreeWidget, QTreeWidgetItem, QToolBar, QToolButton,
    QColorDialog, QPlainTextEdit, QFrame, QCompleter, QSizePolicy, QHeaderView)
from PySide6.QtCore import (Qt, QUrl, QTimer, QSettings, QPropertyAnimation,
    QEasingCurve, QSize, QRectF, QPointF, QStringListModel, QMimeData, Signal)
from PySide6.QtGui import (QFont, QAction, QPixmap, QPen, QBrush, QColor,
    QKeySequence, QTextCharFormat, QTextCursor, QPainter, QPalette, QDrag,
    QTextDocument, QIcon)

# =====================================================================
# CONSTANTS
# =====================================================================
THEMES = {
    "Dark": {"Window":"#1e1e1e","WindowText":"#d4d4d4","Base":"#252526",
             "AlternateBase":"#2d2d30","Text":"#d4d4d4","Button":"#3c3c3c",
             "ButtonText":"#cccccc","Highlight":"#264f78","HighlightedText":"#ffffff",
             "Link":"#3794ff","PlaceholderText":"#6a737d","Accent":"#4CAF50",
             "Error":"#f48771","Warning":"#cca700"},
    "Light": {"Window":"#f3f3f3","WindowText":"#333333","Base":"#ffffff",
              "AlternateBase":"#f5f5f5","Text":"#333333","Button":"#e1e1e1",
              "ButtonText":"#333333","Highlight":"#0078d4","HighlightedText":"#ffffff",
              "Link":"#0066cc","PlaceholderText":"#767676","Accent":"#4CAF50",
              "Error":"#e51400","Warning":"#bf8803"},
    "Nord": {"Window":"#2E3440","WindowText":"#D8DEE9","Base":"#3B4252",
             "AlternateBase":"#434C5E","Text":"#D8DEE9","Button":"#434C5E",
             "ButtonText":"#D8DEE9","Highlight":"#88C0D0","HighlightedText":"#2E3440",
             "Link":"#88C0D0","PlaceholderText":"#4C566A","Accent":"#A3BE8C",
             "Error":"#BF616A","Warning":"#EBCB8B"}
}

CATEGORIES = {
    "General":{"color":"#2196F3","icon":"📄"},"Start":{"color":"#00BCD4","icon":"🎬"},
    "Dialogue":{"color":"#9C27B0","icon":"💬"},"Combat":{"color":"#F44336","icon":"⚔️"},
    "Puzzle":{"color":"#FF9800","icon":"🧩"},"Exploration":{"color":"#4CAF50","icon":"🗺️"},
    "Cutscene":{"color":"#607D8B","icon":"🎥"},"Ending":{"color":"#795548","icon":"🏁"}
}

SCENE_STATUS = {
    "draft": {"icon": "📝", "color": "#9E9E9E", "label": "Draft"},
    "in_progress": {"icon": "🔄", "color": "#FF9800", "label": "In Progress"},
    "review": {"icon": "👀", "color": "#2196F3", "label": "Review"},
    "complete": {"icon": "✅", "color": "#4CAF50", "label": "Complete"},
    "archived": {"icon": "📦", "color": "#607D8B", "label": "Archived"}
}

TRANSITIONS = ["fade","slide-left","slide-right","slide-up","zoom","dissolve","none"]
EFFECTS = ["none","rain","snow","fog","fireflies","dust","embers"]
MAX_UNDO = 50
AUTOSAVE_INTERVAL = 60000

# =====================================================================
# DEFAULT STORY
# =====================================================================
def get_default_story():
    return {
        "title":"The Cursed Temple","author":"Adventure Creator",
        "description":"An ancient temple holds secrets and dangers...",
        "start_scene":"start","languages":{"en":"English"},"current_language":"en",
        "variables":{
            "health":{"default":100,"min":0,"max":100},
            "gold":{"default":0,"min":0,"max":9999},
            "mana":{"default":50,"min":0,"max":100}
        },
        "inventory":{
            "health_potion":{"name":"Health Potion","description":"Restores 50 HP","icon":"🧪","max_stack":10},
            "old_key":{"name":"Rusty Key","description":"Opens the iron door","icon":"🗝️","max_stack":1}
        },
        "characters":{
            "hero":{"name":"Hero","portrait":"","stats":{"hp":100,"mp":50,"attack":10,"defense":5}},
            "guardian":{"name":"Temple Guardian","portrait":"","stats":{"hp":200,"mp":100,"attack":20,"defense":10}}
        },
        "relationships":{
            "hero_guardian":{"char1":"hero","char2":"guardian","value":50,"min":0,"max":100}
        },
        "quests":{
            "find_treasure":{"name":"Find the Treasure","description":"Locate the temple's hidden treasure",
                            "objectives":["Find machete","Find key","Reach treasure room"],"completed":False,
                            "completion_tags":"has_machete,has_key,reached_treasure"}
        },
        "time_system":{"enabled":True,"current_hour":8,"current_day":1,"hours_per_scene":1},
        "chapters":{
            "ch1":{"name":"Chapter 1: The Arrival","scenes":["start","outside_search"]},
            "ch2":{"name":"Chapter 2: The Temple","scenes":["temple_hall"]}
        },
        "map_locations":{
            "entrance":{"name":"Temple Entrance","x":100,"y":100,"visited":True},
            "hall":{"name":"Grand Hall","x":300,"y":100,"visited":False}
        },
        "bookmarks":[],"word_goal":5000,"version_snapshots":{},
        "codex":{
            "temple_lore":{"name":"Temple Lore","icon":"📜","unlock_tag":"saw_warning",
                          "text":"The temple was built by an ancient civilization..."}
        },
        "achievements":[
            {"id":"first_step","name":"First Step","description":"Enter the temple","icon":"🚪"},
            {"id":"treasure","name":"Treasure Hunter","description":"Find the treasure","icon":"💰"}
        ],
        "ending_gallery":{},
        "templates":{
            "basic_choice":{"name":"Basic Choice Scene","data":{
                "title":"New Scene","category":"General","status":"draft","text":"",
                "transition":"fade","effect":"none","options":[
                    {"text":"Continue","target":"","requires_tags":"","grants_tags":"","variable_changes":""}
                ]}}
        },
        "scenes":{
            "start":{"title":"The Jungle Entrance","category":"Start","chapter":"ch1","status":"complete",
                "text":"You stand before the crumbling entrance.\n\nYour health: **{health}**\nGold: *{gold}*\n\nSee [[temple_hall]] for more.",
                "transition":"fade","effect":"fog","image":"","notes":"Opening scene",
                "bgm":"","sfx":"","requires_tags":"","grants_tags":"",
                "variable_changes":"","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":1,"map_marker":"entrance",
                "todos":[{"text":"Add description","done":True},{"text":"Add image","done":False}],
                "dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[
                    {"text":"Enter the temple","target":"temple_hall","requires_tags":"",
                     "grants_tags":"entered_temple","variable_changes":"health-10",
                     "timer":0,"random_targets":"","skill_check":"","success_target":"","failure_target":"",
                     "achievement":"first_step","sfx":"","on_click_script":"","translations":{}},
                    {"text":"Search outside","target":"outside_search","requires_tags":"",
                     "grants_tags":"saw_warning","variable_changes":"",
                     "timer":0,"random_targets":"","skill_check":"","success_target":"","failure_target":"",
                     "achievement":"","sfx":"","on_click_script":"","translations":{}}
                ]},
            "outside_search":{"title":"Outside the Temple","category":"Exploration","chapter":"ch1","status":"in_progress",
                "text":"You find a warning carved into a tree and a rusty key!\n\n{if has_key}You already have the key.{endif}",
                "transition":"slide-left","effect":"fireflies",
                "image":"","notes":"","bgm":"","sfx":"","requires_tags":"","grants_tags":"has_key",
                "variable_changes":"","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":1,"map_marker":"",
                "todos":[],"dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[
                    {"text":"Enter the temple","target":"temple_hall","requires_tags":"",
                     "grants_tags":"entered_temple","variable_changes":"",
                     "timer":0,"random_targets":"","skill_check":"","success_target":"","failure_target":"",
                     "achievement":"","sfx":"","on_click_script":"","translations":{}}
                ]},
            "temple_hall":{"title":"The Grand Hall","category":"Exploration","chapter":"ch2","status":"draft",
                "text":"A massive hall with a **glowing gem** on a pedestal.\n\n{if health<50}You feel weak...{endif}",
                "transition":"zoom","effect":"dust",
                "image":"","notes":"","bgm":"","sfx":"","requires_tags":"","grants_tags":"",
                "variable_changes":"","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":2,"map_marker":"hall",
                "todos":[],"dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[
                    {"text":"Take the gem (Dex 15+)","target":"trap_end","requires_tags":"",
                     "grants_tags":"","variable_changes":"gold+100",
                     "timer":5,"random_targets":"","skill_check":"dexterity>=15",
                     "success_target":"treasure_room","failure_target":"trap_end",
                     "achievement":"","sfx":"","on_click_script":"","translations":{}},
                    {"text":"Use key on iron door","target":"secret_vault","requires_tags":"has_key",
                     "grants_tags":"reached_treasure","variable_changes":"",
                     "timer":0,"random_targets":"","skill_check":"",
                     "success_target":"","failure_target":"",
                     "achievement":"treasure","sfx":"","on_click_script":"","translations":{}}
                ]},
            "treasure_room":{"title":"The Treasure Room","category":"Ending","chapter":"ch2","status":"complete",
                "text":"You found the treasure! Quest complete.\n\nFinal gold: **{gold}**",
                "transition":"fade","effect":"none",
                "image":"","notes":"","bgm":"","sfx":"","requires_tags":"","grants_tags":"",
                "variable_changes":"","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":0,"map_marker":"",
                "todos":[],"dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[],"ending_id":"treasure_ending","ending_title":"The Treasure Hunter"},
            "trap_end":{"title":"Game Over","category":"Ending","chapter":"ch2","status":"complete",
                "text":"The ceiling collapses. You lose.\n\nFinal gold: {gold}",
                "transition":"dissolve","effect":"none",
                "image":"","notes":"","bgm":"","sfx":"","requires_tags":"","grants_tags":"",
                "variable_changes":"","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":0,"map_marker":"",
                "todos":[],"dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[],"ending_id":"death_ending","ending_title":"A Terrible Mistake"},
            "secret_vault":{"title":"The Secret Vault","category":"Ending","chapter":"ch2","status":"complete",
                "text":"The key fits! Inside is the ultimate artifact.\n\nYou win!\n\nFinal gold: {gold}",
                "transition":"fade","effect":"none",
                "image":"","notes":"","bgm":"","sfx":"","requires_tags":"","grants_tags":"",
                "variable_changes":"gold+500","variable_conditions":"",
                "on_enter_script":"","on_exit_script":"",
                "time_advance":0,"map_marker":"",
                "todos":[],"dialogue":[],"combat":{},"comments":[],"locked":False,"translations":{},
                "options":[],"ending_id":"vault_ending","ending_title":"The Secret Vault"}
        }
    }

# =====================================================================
# UTILITIES
# =====================================================================
def parse_tags(s):
    if not s: return []
    return [t.strip().lower() for t in s.split(',') if t.strip()]

def check_tags(pt, r):
    for t in parse_tags(r):
        if t.startswith("!"):
            if t[1:] in pt: return False
        elif t not in pt: return False
    return True

def apply_tags(pt, g):
    for t in parse_tags(g):
        if t.startswith("-"): pt.discard(t[1:])
        else: pt.add(t)

def apply_var_changes(variables, cs):
    if not cs: return
    for c in cs.split(','):
        c = c.strip()
        if not c: continue
        for op in ['+','-','*','/']:
            if op in c:
                p = c.split(op)
                if len(p)==2:
                    try:
                        v = variables.get(p[0].strip())
                        if v:
                            cur = v.get("value",v.get("default",0))
                            val = int(p[1].strip())
                            if op=='+': cur+=val
                            elif op=='-': cur-=val
                            elif op=='*': cur*=val
                            elif op=='/': cur=int(cur/val) if val else cur
                            v["value"]=max(v.get("min",0),min(v.get("max",9999),cur))
                    except: pass
                break

def check_var_cond(variables, cs):
    if not cs: return True
    for c in cs.split(','):
        c=c.strip()
        if not c: continue
        for op in ['>=','<=','!=','>','<','=']:
            if op in c:
                p=c.split(op)
                if len(p)==2:
                    try:
                        v=variables.get(p[0].strip())
                        if v:
                            cur=v.get("value",v.get("default",0))
                            val=int(p[1].strip())
                            ok={'>':cur>val,'<':cur<val,'>=':cur>=val,'<=':cur<=val,
                                '=':cur==val,'!=':cur!=val}
                            if not ok.get(op,True): return False
                    except: pass
                break
    return True

def render_markdown(text, variables=None, tags=None):
    if variables is None: variables = {}
    if tags is None: tags = set()
    
    def rep_cond(m):
        cond, content = m.group(1), m.group(2)
        return content if check_tags(tags,cond) or check_var_cond(variables,cond) else ""
    text = re.sub(r'\{if\s+([^}]+)\}(.*?)\{endif\}', rep_cond, text, flags=re.DOTALL)
    
    def rep_var(m):
        v = variables.get(m.group(1))
        return str(v.get("value",v.get("default",0))) if v else m.group(0)
    text = re.sub(r'\{(\w+)\}', rep_var, text)
    
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b style="color:#4CAF50;">\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
    text = re.sub(r'`(.+?)`', r'<code style="background:#333;padding:2px 6px;border-radius:3px;color:#ff9800;">\1</code>', text)
    
    def rep_link(m):
        scene_id = m.group(1)
        return f'<a href="scene:{scene_id}" style="color:#4CAF50;text-decoration:underline;">→ {scene_id}</a>'
    text = re.sub(r'\[\[([^\]]+)\]\]', rep_link, text)
    
    text = text.replace('\n', '<br>')
    return text

def calc_reading_time(text):
    words = len(text.split())
    minutes = words / 200.0
    if minutes < 1: return f"{int(minutes*60)}s"
    return f"{int(minutes)}m {int((minutes%1)*60)}s"

def collect_all_tags(story_data):
    tags = set()
    for scene in story_data.get("scenes", {}).values():
        tags.update(parse_tags(scene.get("requires_tags", "")))
        tags.update(parse_tags(scene.get("grants_tags", "")))
        for opt in scene.get("options", []):
            tags.update(parse_tags(opt.get("requires_tags", "")))
            tags.update(parse_tags(opt.get("grants_tags", "")))
    return sorted([t for t in tags if not t.startswith("!") and not t.startswith("-")])

# =====================================================================
# AUTO-COMPLETE TEXT EDITOR
# =====================================================================
class AutoCompleteTextEdit(QPlainTextEdit):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)
        self.setFont(QFont("Consolas", 11))
        self.setTabStopDistance(40)
    
    def update_completions(self):
        completions = []
        cursor_pos = self.textCursor().position()
        text_before = self.toPlainText()[:cursor_pos]
        
        if '{' in text_before and not text_before.rstrip().endswith('{if'):
            last_brace = text_before.rfind('{')
            prefix = text_before[last_brace+1:]
            if ' ' not in prefix and '}' not in prefix:
                for var_name in self.editor.story_data.get("variables", {}).keys():
                    completions.append(var_name)
        
        if '[[' in text_before:
            last_bracket = text_before.rfind('[[')
            prefix = text_before[last_bracket+2:]
            if ']]' not in prefix:
                for scene_id in self.editor.story_data.get("scenes", {}).keys():
                    completions.append(scene_id + "]]")
        
        model = QStringListModel(list(set(completions)))
        self.completer.setModel(model)
    
    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape,
                              Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return
        
        super().keyPressEvent(event)
        
        if event.key() in (Qt.Key_BraceLeft, Qt.Key_BracketLeft) or (event.text() and event.text().isalnum()):
            self.update_completions()
            cursor = self.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            prefix = cursor.selectedText()
            if prefix:
                self.completer.setCompletionPrefix(prefix)
                popup = self.completer.popup()
                cursor_rect = self.cursorRect()
                cursor_rect.setWidth(popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width())
                self.completer.complete(cursor_rect)
            else:
                self.completer.popup().hide()
    
    def insert_completion(self, completion):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(completion)
        self.setTextCursor(cursor)

# =====================================================================
# LIVE PREVIEW
# =====================================================================
class LivePreview(QWidget):
    link_clicked = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("👁️ Live Preview")
        header.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 8px; background: #2a2a2a;")
        layout.addWidget(header)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit { background-color: #1a1a1a; color: #e0e0e0;
                       border: none; padding: 15px; font-size: 14px; line-height: 1.6; }
        """)
        self.preview.anchorClicked.connect(self.on_link_clicked)
        layout.addWidget(self.preview)
    
    def on_link_clicked(self, url):
        url_str = url.toString()
        if url_str.startswith("scene:"):
            self.link_clicked.emit(url_str[6:])
    
    def update_preview(self, scene_data, variables=None, tags=None):
        if variables is None: variables = {}
        if tags is None: tags = set()
        
        html = f'<h2 style="color:#4CAF50;margin-bottom:15px;">{scene_data.get("title", "Untitled")}</h2>'
        html += f'<div style="line-height:1.6;">{render_markdown(scene_data.get("text", ""), variables, tags)}</div>'
        
        options = scene_data.get("options", [])
        if options:
            html += '<div style="margin-top:20px;border-top:1px solid #333;padding-top:15px;">'
            html += '<div style="color:#888;font-size:11px;margin-bottom:10px;">CHOICES</div>'
            for opt in options:
                target = opt.get("target", "")
                html += f'<div style="background:#2a2a2a;padding:10px;margin:5px 0;border-radius:4px;border-left:3px solid #4CAF50;">'
                html += f'{opt.get("text", "")} <span style="color:#666;">→ {target}</span></div>'
            html += '</div>'
        
        self.preview.setHtml(html)

# =====================================================================
# TAG BROWSER
# =====================================================================
class TagBrowser(QWidget):
    tag_selected = Signal(str)
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        header = QLabel("🏷️ Tag Browser")
        header.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter tags...")
        self.search.textChanged.connect(self.refresh)
        self.search.setStyleSheet("padding: 5px;")
        layout.addWidget(self.search)
        
        self.tag_list = QListWidget()
        self.tag_list.itemClicked.connect(self.on_tag_clicked)
        layout.addWidget(self.tag_list)
        
        self.count_label = QLabel("0 tags")
        self.count_label.setStyleSheet("color: #888; font-size: 11px; padding: 3px;")
        layout.addWidget(self.count_label)
        
        self.refresh()
    
    def refresh(self):
        self.tag_list.clear()
        filter_text = self.search.text().lower()
        
        tag_counts = {}
        for scene in self.editor.story_data.get("scenes", {}).values():
            for tag in parse_tags(scene.get("grants_tags", "")):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            for opt in scene.get("options", []):
                for tag in parse_tags(opt.get("grants_tags", "")):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        all_tags = collect_all_tags(self.editor.story_data)
        for tag in all_tags:
            if filter_text and filter_text not in tag.lower():
                continue
            count = tag_counts.get(tag, 0)
            item = QListWidgetItem(f"🏷️ {tag} ({count})")
            item.setData(Qt.UserRole, tag)
            self.tag_list.addItem(item)
        
        self.count_label.setText(f"{len(all_tags)} tags total")
    
    def on_tag_clicked(self, item):
        tag = item.data(Qt.UserRole)
        self.tag_selected.emit(tag)

# =====================================================================
# TODO WIDGET
# =====================================================================
class TodoWidget(QWidget):
    def __init__(self, scene_data, parent=None):
        super().__init__(parent)
        self.scene_data = scene_data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("📋 TODOs"))
        add_btn = QPushButton("+")
        add_btn.setFixedSize(25, 25)
        add_btn.clicked.connect(self.add_todo)
        header.addWidget(add_btn)
        header.addStretch()
        layout.addLayout(header)
        
        self.todo_list = QListWidget()
        self.todo_list.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.todo_list)
        
        self.refresh()
    
    def refresh(self):
        self.todo_list.blockSignals(True)
        self.todo_list.clear()
        for i, todo in enumerate(self.scene_data.get("todos", [])):
            item = QListWidgetItem(todo.get("text", ""))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if todo.get("done") else Qt.Unchecked)
            item.setData(Qt.UserRole, i)
            self.todo_list.addItem(item)
        self.todo_list.blockSignals(False)
    
    def add_todo(self):
        text, ok = QInputDialog.getText(self, "Add TODO", "Task:")
        if ok and text:
            self.scene_data.setdefault("todos", []).append({"text": text, "done": False})
            self.refresh()
    
    def on_item_changed(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None and idx < len(self.scene_data.get("todos", [])):
            self.scene_data["todos"][idx]["done"] = item.checkState() == Qt.Checked

# =====================================================================
# TEMPLATE MANAGER
# =====================================================================
class TemplateManager(QWidget):
    template_selected = Signal(dict)
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        header = QLabel("📋 Templates")
        header.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self.on_template_double_clicked)
        layout.addWidget(self.template_list)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Current")
        save_btn.clicked.connect(self.save_template)
        del_btn = QPushButton("🗑️")
        del_btn.clicked.connect(self.delete_template)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        self.refresh()
    
    def refresh(self):
        self.template_list.clear()
        templates = self.editor.story_data.get("templates", {})
        for tid, tdata in templates.items():
            item = QListWidgetItem(f"📋 {tdata.get('name', tid)}")
            item.setData(Qt.UserRole, tid)
            self.template_list.addItem(item)
    
    def save_template(self):
        if not self.editor.current_scene_id:
            QMessageBox.information(self, "No Scene", "Open a scene first.")
            return
        name, ok = QInputDialog.getText(self, "Save Template", "Template name:")
        if ok and name:
            tid = f"template_{uuid.uuid4().hex[:6]}"
            scene = copy.deepcopy(self.editor.story_data["scenes"][self.editor.current_scene_id])
            scene["title"] = "New Scene"
            scene["text"] = ""
            scene["options"] = []
            self.editor.story_data.setdefault("templates", {})[tid] = {"name": name, "data": scene}
            self.refresh()
    
    def on_template_double_clicked(self, item):
        tid = item.data(Qt.UserRole)
        template = self.editor.story_data.get("templates", {}).get(tid)
        if template:
            self.template_selected.emit(copy.deepcopy(template["data"]))
    
    def delete_template(self):
        item = self.template_list.currentItem()
        if not item: return
        tid = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Delete", "Delete template?") == QMessageBox.Yes:
            del self.editor.story_data["templates"][tid]
            self.refresh()

# =====================================================================
# CHOICE WIDGET
# =====================================================================
class ChoiceWidget(QWidget):
    delete_requested = Signal(object)
    changed = Signal()
    
    def __init__(self, scene_ids, editor, data=None, parent=None):
        super().__init__(parent)
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        main_row = QHBoxLayout()
        
        self.drag_handle = QLabel("⋮⋮")
        self.drag_handle.setStyleSheet("color: #666; padding: 0 5px;")
        self.drag_handle.setToolTip("Drag to reorder")
        main_row.addWidget(self.drag_handle)
        
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Choice text...")
        self.text_edit.textChanged.connect(self.emit_changed)
        main_row.addWidget(self.text_edit, stretch=3)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(scene_ids)
        self.target_combo.currentTextChanged.connect(self.emit_changed)
        main_row.addWidget(self.target_combo, stretch=2)
        
        adv_btn = QPushButton("⚙️")
        adv_btn.setFixedSize(30, 30)
        adv_btn.setToolTip("Advanced options")
        adv_btn.clicked.connect(self.show_advanced)
        main_row.addWidget(adv_btn)
        
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(30, 30)
        del_btn.setStyleSheet("background: #f44336; color: white; border-radius: 15px;")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self))
        main_row.addWidget(del_btn)
        
        layout.addLayout(main_row)
        
        self.adv_widget = QWidget()
        adv_layout = QGridLayout(self.adv_widget)
        adv_layout.setContentsMargins(25, 0, 0, 0)
        
        self.req_tags = QLineEdit(); self.req_tags.setPlaceholderText("Requires tags")
        self.req_tags.textChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Req:"), 0, 0); adv_layout.addWidget(self.req_tags, 0, 1)
        
        self.grant_tags = QLineEdit(); self.grant_tags.setPlaceholderText("Grants tags")
        self.grant_tags.textChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Grant:"), 1, 0); adv_layout.addWidget(self.grant_tags, 1, 1)
        
        self.var_changes = QLineEdit(); self.var_changes.setPlaceholderText("health-10, gold+5")
        self.var_changes.textChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Vars:"), 2, 0); adv_layout.addWidget(self.var_changes, 2, 1)
        
        self.timer_spin = QSpinBox(); self.timer_spin.setRange(0, 60); self.timer_spin.setSuffix(" sec")
        self.timer_spin.valueChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Timer:"), 3, 0); adv_layout.addWidget(self.timer_spin, 3, 1)
        
        self.skill_check = QLineEdit(); self.skill_check.setPlaceholderText("dexterity>=15")
        self.skill_check.textChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Skill:"), 4, 0); adv_layout.addWidget(self.skill_check, 4, 1)
        
        self.success_target = QComboBox(); self.success_target.addItems([""] + scene_ids)
        self.success_target.currentTextChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Success→"), 5, 0); adv_layout.addWidget(self.success_target, 5, 1)
        
        self.failure_target = QComboBox(); self.failure_target.addItems([""] + scene_ids)
        self.failure_target.currentTextChanged.connect(self.emit_changed)
        adv_layout.addWidget(QLabel("Failure→"), 6, 0); adv_layout.addWidget(self.failure_target, 6, 1)
        
        self.adv_widget.setVisible(False)
        layout.addWidget(self.adv_widget)
        
        if data:
            self.text_edit.setText(data.get("text", ""))
            self.req_tags.setText(data.get("requires_tags", ""))
            self.grant_tags.setText(data.get("grants_tags", ""))
            self.var_changes.setText(data.get("variable_changes", ""))
            self.timer_spin.setValue(data.get("timer", 0))
            self.skill_check.setText(data.get("skill_check", ""))
            target = data.get("target", "")
            if target in scene_ids: self.target_combo.setCurrentText(target)
            st = data.get("success_target", "")
            if st in scene_ids: self.success_target.setCurrentText(st)
            ft = data.get("failure_target", "")
            if ft in scene_ids: self.failure_target.setCurrentText(ft)
    
    def emit_changed(self):
        self.changed.emit()
    
    def show_advanced(self):
        self.adv_widget.setVisible(not self.adv_widget.isVisible())
    
    def get_data(self):
        return {
            "text": self.text_edit.text(),
            "target": self.target_combo.currentText(),
            "requires_tags": self.req_tags.text(),
            "grants_tags": self.grant_tags.text(),
            "variable_changes": self.var_changes.text(),
            "timer": self.timer_spin.value(),
            "random_targets": "",
            "skill_check": self.skill_check.text(),
            "success_target": self.success_target.currentText(),
            "failure_target": self.failure_target.currentText(),
            "achievement": "", "sfx": "", "on_click_script": "", "translations": {}
        }

# =====================================================================
# SCENE TAB
# =====================================================================
class SceneTab(QWidget):
    def __init__(self, scene_id, editor, parent=None):
        super().__init__(parent)
        self.scene_id = scene_id
        self.editor = editor
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        scene = self.editor.story_data["scenes"][self.scene_id]
        
        # Top bar
        top_bar = QHBoxLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setText(scene.get("title", ""))
        self.title_edit.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_edit.setStyleSheet("""
            QLineEdit { background: transparent; border: none;
                       border-bottom: 2px solid #4CAF50; padding: 5px; color: white; }
        """)
        self.title_edit.textChanged.connect(self.on_title_changed)
        top_bar.addWidget(self.title_edit, stretch=1)
        
        self.status_combo = QComboBox()
        for sid, sdata in SCENE_STATUS.items():
            self.status_combo.addItem(f"{sdata['icon']} {sdata['label']}", sid)
        idx = self.status_combo.findData(scene.get("status", "draft"))
        if idx >= 0: self.status_combo.setCurrentIndex(idx)
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        top_bar.addWidget(self.status_combo)
        
        dup_btn = QPushButton("📋")
        dup_btn.setToolTip("Duplicate")
        dup_btn.clicked.connect(lambda: self.editor.duplicate_scene(self.scene_id))
        top_bar.addWidget(dup_btn)
        
        layout.addLayout(top_bar)
        
        # Meta row
        meta = QHBoxLayout()
        meta.addWidget(QLabel("Category:"))
        self.cat_combo = QComboBox()
        for c, d in CATEGORIES.items():
            self.cat_combo.addItem(f"{d['icon']} {c}", c)
        idx = self.cat_combo.findData(scene.get("category", "General"))
        if idx >= 0: self.cat_combo.setCurrentIndex(idx)
        self.cat_combo.currentIndexChanged.connect(self.on_category_changed)
        meta.addWidget(self.cat_combo)
        
        meta.addWidget(QLabel("Chapter:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.addItem("(No chapter)","")
        for cid, cdata in self.editor.story_data.get("chapters", {}).items():
            self.chapter_combo.addItem(cdata.get("name", cid), cid)
        idx = self.chapter_combo.findData(scene.get("chapter", ""))
        if idx >= 0: self.chapter_combo.setCurrentIndex(idx)
        self.chapter_combo.currentIndexChanged.connect(self.on_chapter_changed)
        meta.addWidget(self.chapter_combo)
        
        meta.addWidget(QLabel("Transition:"))
        self.trans_combo = QComboBox()
        self.trans_combo.addItems(TRANSITIONS)
        self.trans_combo.setCurrentText(scene.get("transition", "fade"))
        self.trans_combo.currentTextChanged.connect(self.on_transition_changed)
        meta.addWidget(self.trans_combo)
        
        meta.addWidget(QLabel("Effect:"))
        self.fx_combo = QComboBox()
        self.fx_combo.addItems(EFFECTS)
        self.fx_combo.setCurrentText(scene.get("effect", "none"))
        self.fx_combo.currentTextChanged.connect(self.on_effect_changed)
        meta.addWidget(self.fx_combo)
        
        layout.addLayout(meta)
        
        # Split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Text editor
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        hint = QLabel("<b>📝 Scene Text</b> <span style='color:#888;font-size:11px;'>(**bold**, *italic*, [[scene]], {var}, {if tag}...{endif})</span>")
        left_layout.addWidget(hint)
        
        self.text_edit = AutoCompleteTextEdit(self.editor)
        self.text_edit.setPlainText(scene.get("text", ""))
        self.text_edit.setPlaceholderText("Write your scene here...")
        self.text_edit.textChanged.connect(self.on_text_changed)
        left_layout.addWidget(self.text_edit)
        
        stats_bar = QHBoxLayout()
        self.word_count = QLabel("0 words")
        self.word_count.setStyleSheet("color: #888; font-size: 11px;")
        stats_bar.addWidget(self.word_count)
        self.reading_time = QLabel("0s read")
        self.reading_time.setStyleSheet("color: #888; font-size: 11px;")
        stats_bar.addWidget(self.reading_time)
        stats_bar.addStretch()
        left_layout.addLayout(stats_bar)
        
        splitter.addWidget(left)
        
        # Right: Live preview
        self.preview = LivePreview()
        self.preview.link_clicked.connect(self.editor.open_scene_tab)
        self.preview.setMinimumWidth(300)
        splitter.addWidget(self.preview)
        
        splitter.setSizes([500, 400])
        layout.addWidget(splitter, stretch=1)
        
        # Bottom tabs
        bottom_tabs = QTabWidget()
        bottom_tabs.setMaximumHeight(280)
        
        # Choices
        choices_widget = QWidget()
        cl = QVBoxLayout(choices_widget)
        self.choices_container = QWidget()
        self.choices_layout = QVBoxLayout(self.choices_container)
        self.choices_layout.setContentsMargins(0, 0, 0, 0)
        self.choices_layout.setAlignment(Qt.AlignTop)
        
        choices_scroll = QScrollArea()
        choices_scroll.setWidgetResizable(True)
        choices_scroll.setWidget(self.choices_container)
        cl.addWidget(choices_scroll)
        
        add_choice_btn = QPushButton("+ Add Choice")
        add_choice_btn.clicked.connect(self.add_choice)
        cl.addWidget(add_choice_btn)
        bottom_tabs.addTab(choices_widget, "🔀 Choices")
        
        # Tags
        tags_widget = QWidget()
        tl = QFormLayout(tags_widget)
        self.req_tags = QLineEdit(); self.req_tags.setText(scene.get("requires_tags", ""))
        self.req_tags.setPlaceholderText("tag1, tag2, !forbidden")
        self.req_tags.textChanged.connect(self.on_req_tags_changed)
        tl.addRow("Requires:", self.req_tags)
        
        self.grant_tags = QLineEdit(); self.grant_tags.setText(scene.get("grants_tags", ""))
        self.grant_tags.setPlaceholderText("tag1, tag2, -remove")
        self.grant_tags.textChanged.connect(self.on_grant_tags_changed)
        tl.addRow("Grants:", self.grant_tags)
        
        self.var_changes = QLineEdit(); self.var_changes.setText(scene.get("variable_changes", ""))
        self.var_changes.setPlaceholderText("health-10, gold+5")
        self.var_changes.textChanged.connect(self.on_var_changes_changed)
        tl.addRow("Variables:", self.var_changes)
        bottom_tabs.addTab(tags_widget, "🏷️ Tags & Vars")
        
        # TODOs
        self.todo_widget = TodoWidget(scene)
        bottom_tabs.addTab(self.todo_widget, "📋 TODOs")
        
        # Notes
        notes_widget = QWidget()
        nl = QVBoxLayout(notes_widget)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(scene.get("notes", ""))
        self.notes_edit.setPlaceholderText("Private notes...")
        self.notes_edit.textChanged.connect(self.on_notes_changed)
        nl.addWidget(self.notes_edit)
        bottom_tabs.addTab(notes_widget, "📝 Notes")
        
        # Scripting
        script_widget = QWidget()
        scl = QVBoxLayout(script_widget)
        scl.addWidget(QLabel("On Enter (JavaScript):"))
        self.on_enter_script = QTextEdit()
        self.on_enter_script.setMaximumHeight(80)
        self.on_enter_script.setPlainText(scene.get("on_enter_script", ""))
        self.on_enter_script.setPlaceholderText("// tags.add('entered')")
        self.on_enter_script.textChanged.connect(self.on_enter_script_changed)
        scl.addWidget(self.on_enter_script)
        scl.addWidget(QLabel("On Exit:"))
        self.on_exit_script = QTextEdit()
        self.on_exit_script.setMaximumHeight(80)
        self.on_exit_script.setPlainText(scene.get("on_exit_script", ""))
        self.on_exit_script.textChanged.connect(self.on_exit_script_changed)
        scl.addWidget(self.on_exit_script)
        bottom_tabs.addTab(script_widget, "⚡ Script")
        
        layout.addWidget(bottom_tabs)
        
        self.update_stats()
        self.update_preview()
        self.load_choices()
    
    def update_stats(self):
        text = self.text_edit.toPlainText()
        wc = len(text.split()) if text.strip() else 0
        self.word_count.setText(f"{wc} words")
        self.reading_time.setText(f"{calc_reading_time(text)} read")
    
    def update_preview(self):
        scene = self.editor.story_data["scenes"][self.scene_id]
        preview_data = {
            "title": self.title_edit.text(),
            "text": self.text_edit.toPlainText(),
            "options": self.get_current_options()
        }
        variables = {}
        for k, v in self.editor.story_data.get("variables", {}).items():
            variables[k] = {"value": v.get("default", 0), "min": v.get("min", 0), "max": v.get("max", 9999)}
        self.preview.update_preview(preview_data, variables, set())
    
    def get_current_options(self):
        options = []
        for i in range(self.choices_layout.count()):
            w = self.choices_layout.itemAt(i).widget()
            if isinstance(w, ChoiceWidget):
                options.append(w.get_data())
        return options
    
    def load_choices(self):
        for i in reversed(range(self.choices_layout.count())):
            self.choices_layout.itemAt(i).widget().deleteLater()
        scene = self.editor.story_data["scenes"][self.scene_id]
        scene_ids = list(self.editor.story_data["scenes"].keys())
        for opt in scene.get("options", []):
            w = ChoiceWidget(scene_ids, self.editor, opt)
            w.delete_requested.connect(self.remove_choice)
            w.changed.connect(self.on_choice_changed)
            self.choices_layout.addWidget(w)
    
    def on_title_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["title"] = text
        idx = self.editor.tab_widget.indexOf(self)
        if idx >= 0:
            self.editor.tab_widget.setTabText(idx, text[:20] + ("..." if len(text) > 20 else ""))
        self.editor.refresh_scene_list()
        self.editor.mark_dirty()
    
    def on_status_changed(self, idx):
        status = self.status_combo.itemData(idx)
        self.editor.story_data["scenes"][self.scene_id]["status"] = status
        self.editor.refresh_scene_list()
        self.editor.mark_dirty()
    
    def on_category_changed(self, idx):
        cat = self.cat_combo.itemData(idx)
        self.editor.story_data["scenes"][self.scene_id]["category"] = cat
        self.editor.refresh_scene_list()
        self.editor.mark_dirty()
    
    def on_chapter_changed(self, idx):
        chapter = self.chapter_combo.itemData(idx)
        self.editor.story_data["scenes"][self.scene_id]["chapter"] = chapter or ""
        self.editor.mark_dirty()
    
    def on_transition_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["transition"] = text
        self.editor.mark_dirty()
    
    def on_effect_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["effect"] = text
        self.editor.mark_dirty()
    
    def on_text_changed(self):
        self.editor.story_data["scenes"][self.scene_id]["text"] = self.text_edit.toPlainText()
        self.update_stats()
        self.update_preview()
        self.editor.mark_dirty()
    
    def on_req_tags_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["requires_tags"] = text
        self.editor.tag_browser.refresh()
        self.editor.mark_dirty()
    
    def on_grant_tags_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["grants_tags"] = text
        self.editor.tag_browser.refresh()
        self.editor.mark_dirty()
    
    def on_var_changes_changed(self, text):
        self.editor.story_data["scenes"][self.scene_id]["variable_changes"] = text
        self.editor.mark_dirty()
    
    def on_notes_changed(self):
        self.editor.story_data["scenes"][self.scene_id]["notes"] = self.notes_edit.toPlainText()
        self.editor.mark_dirty()
    
    def on_enter_script_changed(self):
        self.editor.story_data["scenes"][self.scene_id]["on_enter_script"] = self.on_enter_script.toPlainText()
        self.editor.mark_dirty()
    
    def on_exit_script_changed(self):
        self.editor.story_data["scenes"][self.scene_id]["on_exit_script"] = self.on_exit_script.toPlainText()
        self.editor.mark_dirty()
    
    def add_choice(self):
        scene_ids = list(self.editor.story_data["scenes"].keys())
        w = ChoiceWidget(scene_ids, self.editor)
        w.delete_requested.connect(self.remove_choice)
        w.changed.connect(self.on_choice_changed)
        self.choices_layout.addWidget(w)
        self.on_choice_changed()
    
    def remove_choice(self, widget):
        widget.deleteLater()
        QTimer.singleShot(0, self.on_choice_changed)
    
    def on_choice_changed(self):
        self.editor.story_data["scenes"][self.scene_id]["options"] = self.get_current_options()
        self.update_preview()
        self.editor.mark_dirty()
    
    def load_scene_data(self):
        scene = self.editor.story_data["scenes"][self.scene_id]
        self.title_edit.setText(scene.get("title", ""))
        self.text_edit.setPlainText(scene.get("text", ""))
        self.req_tags.setText(scene.get("requires_tags", ""))
        self.grant_tags.setText(scene.get("grants_tags", ""))
        self.var_changes.setText(scene.get("variable_changes", ""))
        self.notes_edit.setPlainText(scene.get("notes", ""))
        self.on_enter_script.setPlainText(scene.get("on_enter_script", ""))
        self.on_exit_script.setPlainText(scene.get("on_exit_script", ""))
        
        idx = self.status_combo.findData(scene.get("status", "draft"))
        if idx >= 0: self.status_combo.setCurrentIndex(idx)
        idx = self.cat_combo.findData(scene.get("category", "General"))
        if idx >= 0: self.cat_combo.setCurrentIndex(idx)
        self.trans_combo.setCurrentText(scene.get("transition", "fade"))
        self.fx_combo.setCurrentText(scene.get("effect", "none"))
        
        self.load_choices()
        self.todo_widget.refresh()
        self.update_stats()
        self.update_preview()

# =====================================================================
# PREVIEW DIALOG
# =====================================================================
class PreviewDialog(QDialog):
    def __init__(self, scene_data, story_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"👁️ Preview: {scene_data.get('title','Scene')}")
        self.resize(800, 600)
        self.story_data = story_data
        self.tags = set()
        self.variables = {}
        for k, v in story_data.get("variables", {}).items():
            self.variables[k] = {"value": v.get("default", 0), "min": v.get("min", 0), "max": v.get("max", 9999)}
        
        layout = QHBoxLayout(self)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit { background: #1a1a1a; color: #e0e0e0;
                       padding: 20px; font-size: 14px; line-height: 1.6; }
        """)
        self.preview.anchorClicked.connect(self.handle_link)
        layout.addWidget(self.preview, stretch=2)
        
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.addWidget(QLabel("<b>🔧 Debugger</b>"))
        rl.addWidget(QLabel("Variables:"))
        self.vars_disp = QTextEdit(); self.vars_disp.setReadOnly(True); self.vars_disp.setMaximumHeight(150)
        rl.addWidget(self.vars_disp)
        rl.addWidget(QLabel("Tags:"))
        self.tags_disp = QTextEdit(); self.tags_disp.setReadOnly(True)
        rl.addWidget(self.tags_disp)
        layout.addWidget(right, stretch=1)
        
        self.current_scene = scene_data
        self.render(scene_data)
    
    def render(self, scene):
        self.current_scene = scene
        html = f'<h2 style="color:#4CAF50;">{scene.get("title", "")}</h2>'
        html += f'<div>{render_markdown(scene.get("text", ""), self.variables, self.tags)}</div>'
        
        options = scene.get("options", [])
        visible = [o for o in options if check_tags(self.tags, o.get("requires_tags", ""))]
        if visible:
            html += '<div style="margin-top:20px;">'
            for i, opt in enumerate(visible, 1):
                target = opt.get("target", "")
                html += f'<div style="background:#2a2a2a;padding:10px;margin:5px 0;border-radius:4px;border-left:3px solid #4CAF50;">'
                html += f'<a href="choice:{i-1}" style="color:white;text-decoration:none;">{i}. {opt.get("text", "")}</a>'
                html += f' <span style="color:#666;">→ {target}</span></div>'
            html += '</div>'
        else:
            html += '<div style="color:#f44336;font-weight:bold;margin-top:20px;">— END —</div>'
        
        self.preview.setHtml(html)
        
        vars_text = "\n".join([f"{k}: {v['value']}" for k, v in self.variables.items()])
        self.vars_disp.setPlainText(vars_text or "(none)")
        self.tags_disp.setPlainText(", ".join(sorted(self.tags)) or "(none)")
    
    def handle_link(self, url):
        url_str = url.toString()
        if url_str.startswith("choice:"):
            idx = int(url_str[7:])
            options = [o for o in self.current_scene.get("options", [])
                      if check_tags(self.tags, o.get("requires_tags", ""))]
            if idx < len(options):
                opt = options[idx]
                apply_tags(self.tags, opt.get("grants_tags", ""))
                apply_var_changes(self.variables, opt.get("variable_changes", ""))
                target = opt.get("target", "")
                if target in self.story_data.get("scenes", {}):
                    self.render(self.story_data["scenes"][target])
        elif url_str.startswith("scene:"):
            scene_id = url_str[6:]
            if scene_id in self.story_data.get("scenes", {}):
                self.render(self.story_data["scenes"][scene_id])

# =====================================================================
# SHORTCUTS OVERLAY
# =====================================================================
class ShortcutsOverlay(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ Keyboard Shortcuts")
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        title = QLabel("⌨️ Keyboard Shortcuts")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        shortcuts = [
            ("General", [
                ("Ctrl+S", "Save story"), ("Ctrl+O", "Load story"), ("Ctrl+E", "Export HTML5"),
                ("Ctrl+Z", "Undo"), ("Ctrl+Shift+Z", "Redo"), ("F1", "Show this help"), ("F5", "Preview scene")
            ]),
            ("Navigation", [
                ("Ctrl+G", "Quick jump to scene"), ("Ctrl+Tab", "Next tab"),
                ("Ctrl+Shift+Tab", "Previous tab"), ("Ctrl+W", "Close current tab"), ("Ctrl+N", "New scene")
            ]),
            ("Editing", [
                ("{", "Trigger variable auto-complete"), ("[[", "Trigger scene link auto-complete"),
                ("**text**", "Bold text"), ("*text*", "Italic text"), ("~~text~~", "Strikethrough"),
                ("`text`", "Code/mono"), ("[[scene_id]]", "Clickable scene link"),
                ("{if tag}...{endif}", "Conditional text"), ("{variable}", "Insert variable value")
            ]),
        ]
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); cl = QVBoxLayout(content)
        
        for section, items in shortcuts:
            section_lbl = QLabel(section)
            section_lbl.setFont(QFont("Arial", 13, QFont.Bold))
            section_lbl.setStyleSheet("color: #4CAF50; margin-top: 15px;")
            cl.addWidget(section_lbl)
            
            for key, desc in items:
                row = QHBoxLayout()
                key_lbl = QLabel(key)
                key_lbl.setStyleSheet("""
                    background: #333; color: #fff; padding: 4px 10px;
                    border-radius: 4px; font-family: Consolas; font-weight: bold;
                    border: 1px solid #555;
                """)
                key_lbl.setFixedWidth(140)
                desc_lbl = QLabel(desc); desc_lbl.setStyleSheet("color: #ccc;")
                row.addWidget(key_lbl); row.addWidget(desc_lbl); row.addStretch()
                w = QWidget(); w.setLayout(row); cl.addWidget(w)
        
        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        close_btn = QPushButton("Close (Esc)")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("background: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(close_btn)

# =====================================================================
# MAIN EDITOR
# =====================================================================
class StoryEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.story_data = get_default_story()
        self.current_scene_id = None
        self.open_tabs = {}
        self.undo_stack = []
        self.redo_stack = []
        self.autosave_dirty = False
        self.init_ui()
        self.refresh_scene_list()
        if self.story_data["scenes"]:
            self.open_scene_tab(self.story_data["start_scene"])
        
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(AUTOSAVE_INTERVAL)
    
    def init_ui(self):
        ml = QHBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        
        # Left panel
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        ll = QVBoxLayout(left_panel)
        ll.setContentsMargins(5, 5, 5, 5)
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search scenes...")
        self.search.textChanged.connect(self.filter_scenes)
        ll.addWidget(self.search)
        
        qa = QHBoxLayout()
        new_btn = QPushButton("+ New Scene")
        new_btn.clicked.connect(self.add_new_scene)
        new_btn.setStyleSheet("background: #4CAF50; color: white;")
        qa.addWidget(new_btn)
        ll.addLayout(qa)
        
        ll.addWidget(QLabel("<b>📚 Scenes</b>"))
        
        self.scene_list = QListWidget()
        self.scene_list.currentItemChanged.connect(self.on_scene_selected)
        self.scene_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_list.customContextMenuRequested.connect(self.show_context_menu)
        self.scene_list.itemDoubleClicked.connect(self.on_scene_double_clicked)
        ll.addWidget(self.scene_list, stretch=2)
        
        self.tag_browser = TagBrowser(self)
        self.tag_browser.tag_selected.connect(self.filter_by_tag)
        ll.addWidget(self.tag_browser, stretch=1)
        
        self.template_manager = TemplateManager(self)
        self.template_manager.template_selected.connect(self.create_from_template)
        ll.addWidget(self.template_manager, stretch=1)
        
        ml.addWidget(left_panel)
        
        # Center: Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        ml.addWidget(self.tab_widget, stretch=1)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_story)
        QShortcut(QKeySequence("Ctrl+N"), self, self.add_new_scene)
        QShortcut(QKeySequence("Ctrl+G"), self, self.quick_jump)
        QShortcut(QKeySequence("F1"), self, self.show_shortcuts)
        QShortcut(QKeySequence("F5"), self, self.preview_current_scene)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
    
    def autosave(self):
        if self.autosave_dirty:
            try:
                settings = QSettings("AdventureCreator", "StoryEditor")
                settings.setValue("autosave", json.dumps(self.get_story_data()))
                settings.setValue("autosave_time", datetime.now().isoformat())
                self.autosave_dirty = False
                if self.window() and hasattr(self.window(), 'update_autosave_indicator'):
                    self.window().update_autosave_indicator(True)
            except: pass
    
    def mark_dirty(self):
        self.autosave_dirty = True
        if self.window() and hasattr(self.window(), 'update_autosave_indicator'):
            self.window().update_autosave_indicator(False)
    
    def push_undo(self):
        self.undo_stack.append(copy.deepcopy(self.story_data))
        if len(self.undo_stack) > MAX_UNDO:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.mark_dirty()
    
    def undo(self):
        if not self.undo_stack: return
        self.redo_stack.append(copy.deepcopy(self.story_data))
        self.story_data = self.undo_stack.pop()
        self.refresh_all()
    
    def redo(self):
        if not self.redo_stack: return
        self.undo_stack.append(copy.deepcopy(self.story_data))
        self.story_data = self.redo_stack.pop()
        self.refresh_all()
    
    def refresh_all(self):
        self.refresh_scene_list()
        self.tag_browser.refresh()
        self.template_manager.refresh()
        if self.current_scene_id and self.current_scene_id in self.open_tabs:
            self.open_tabs[self.current_scene_id].load_scene_data()
    
    def open_scene_tab(self, scene_id):
        if scene_id not in self.story_data["scenes"]: return
        
        if scene_id in self.open_tabs:
            idx = self.tab_widget.indexOf(self.open_tabs[scene_id])
            self.tab_widget.setCurrentIndex(idx)
        else:
            tab = SceneTab(scene_id, self)
            self.open_tabs[scene_id] = tab
            scene = self.story_data["scenes"][scene_id]
            status_icon = SCENE_STATUS.get(scene.get("status", "draft"), SCENE_STATUS["draft"])["icon"]
            title = scene["title"][:20] + ("..." if len(scene["title"]) > 20 else "")
            self.tab_widget.addTab(tab, f"{status_icon} {title}")
            self.tab_widget.setCurrentWidget(tab)
        
        self.current_scene_id = scene_id
        
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            if item.data(Qt.UserRole) == scene_id:
                self.scene_list.setCurrentItem(item)
                break
    
    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        for sid, tab in list(self.open_tabs.items()):
            if tab == widget:
                del self.open_tabs[sid]
                break
        self.tab_widget.removeTab(index)
    
    def close_current_tab(self):
        idx = self.tab_widget.currentIndex()
        if idx >= 0:
            self.close_tab(idx)
    
    def on_tab_changed(self, index):
        widget = self.tab_widget.widget(index)
        if widget and isinstance(widget, SceneTab):
            self.current_scene_id = widget.scene_id
            for i in range(self.scene_list.count()):
                item = self.scene_list.item(i)
                if item.data(Qt.UserRole) == self.current_scene_id:
                    self.scene_list.blockSignals(True)
                    self.scene_list.setCurrentItem(item)
                    self.scene_list.blockSignals(False)
                    break
    
    def on_scene_selected(self, current, previous):
        if current:
            scene_id = current.data(Qt.UserRole)
            if scene_id:
                self.open_scene_tab(scene_id)
    
    def on_scene_double_clicked(self, item):
        scene_id = item.data(Qt.UserRole)
        if scene_id:
            self.open_scene_tab(scene_id)
    
    def show_context_menu(self, pos):
        item = self.scene_list.itemAt(pos)
        if not item: return
        scene_id = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        menu.addAction("📂 Open in Tab", lambda: self.open_scene_tab(scene_id))
        menu.addSeparator()
        menu.addAction("📋 Duplicate", lambda: self.duplicate_scene(scene_id))
        
        bm = self.story_data.get("bookmarks", [])
        if scene_id in bm:
            menu.addAction("⭐ Remove Bookmark", lambda: self.toggle_bookmark(scene_id))
        else:
            menu.addAction("⭐ Add Bookmark", lambda: self.toggle_bookmark(scene_id))
        
        locked = self.story_data["scenes"].get(scene_id, {}).get("locked", False)
        menu.addAction("🔓 Unlock" if locked else "🔒 Lock", lambda: self.toggle_lock(scene_id))
        
        status_menu = menu.addMenu("📊 Set Status")
        for sid, sdata in SCENE_STATUS.items():
            status_menu.addAction(f"{sdata['icon']} {sdata['label']}",
                                 lambda s=sid: self.set_status(scene_id, s))
        
        menu.addSeparator()
        menu.addAction("👁️ Preview", lambda: self.preview_scene(scene_id))
        menu.addSeparator()
        menu.addAction("🗑️ Delete", lambda: self.delete_scene(scene_id))
        
        menu.exec(self.scene_list.viewport().mapToGlobal(pos))
    
    def toggle_bookmark(self, scene_id):
        bm = self.story_data.setdefault("bookmarks", [])
        if scene_id in bm: bm.remove(scene_id)
        else: bm.append(scene_id)
        self.refresh_scene_list()
        self.mark_dirty()
    
    def toggle_lock(self, scene_id):
        scene = self.story_data["scenes"][scene_id]
        scene["locked"] = not scene.get("locked", False)
        self.refresh_scene_list()
        self.mark_dirty()
    
    def set_status(self, scene_id, status):
        self.story_data["scenes"][scene_id]["status"] = status
        self.refresh_scene_list()
        if scene_id in self.open_tabs:
            tab = self.open_tabs[scene_id]
            idx = tab.status_combo.findData(status)
            if idx >= 0:
                tab.status_combo.blockSignals(True)
                tab.status_combo.setCurrentIndex(idx)
                tab.status_combo.blockSignals(False)
        self.mark_dirty()
    
    def duplicate_scene(self, scene_id):
        self.push_undo()
        nid = f"scene_{uuid.uuid4().hex[:6]}"
        ns = copy.deepcopy(self.story_data["scenes"][scene_id])
        ns["title"] += " (Copy)"
        self.story_data["scenes"][nid] = ns
        self.refresh_scene_list()
        self.open_scene_tab(nid)
    
    def delete_scene(self, scene_id):
        if len(self.story_data["scenes"]) <= 1:
            QMessageBox.warning(self, "Error", "Need at least one scene.")
            return
        if QMessageBox.question(self, "Delete", "Delete this scene?") != QMessageBox.Yes:
            return
        self.push_undo()
        del self.story_data["scenes"][scene_id]
        if self.story_data["start_scene"] == scene_id:
            self.story_data["start_scene"] = list(self.story_data["scenes"].keys())[0]
        if scene_id in self.open_tabs:
            idx = self.tab_widget.indexOf(self.open_tabs[scene_id])
            self.close_tab(idx)
        self.refresh_scene_list()
    
    def preview_scene(self, scene_id):
        scene = self.story_data["scenes"][scene_id]
        dlg = PreviewDialog(scene, self.story_data, self)
        dlg.exec()
    
    def preview_current_scene(self):
        if self.current_scene_id:
            self.preview_scene(self.current_scene_id)
    
    def create_from_template(self, template_data):
        self.push_undo()
        nid = f"scene_{uuid.uuid4().hex[:6]}"
        ns = copy.deepcopy(template_data)
        self.story_data["scenes"][nid] = ns
        self.refresh_scene_list()
        self.open_scene_tab(nid)
    
    def filter_by_tag(self, tag):
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            scene_id = item.data(Qt.UserRole)
            scene = self.story_data["scenes"][scene_id]
            has_tag = (tag in parse_tags(scene.get("grants_tags", "")) or
                      tag in parse_tags(scene.get("requires_tags", "")))
            item.setHidden(not has_tag)
    
    def filter_scenes(self, text):
        text = text.lower()
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            scene_id = item.data(Qt.UserRole)
            scene = self.story_data["scenes"][scene_id]
            searchable = f"{scene['title']} {scene.get('text','')} {scene_id}"
            item.setHidden(text not in searchable.lower())
    
    def refresh_scene_list(self):
        current_id = self.current_scene_id
        self.scene_list.clear()
        bm = self.story_data.get("bookmarks", [])
        
        scenes = list(self.story_data["scenes"].items())
        scenes.sort(key=lambda x: (x[0] not in bm, x[1]["title"].lower()))
        
        for scene_id, scene in scenes:
            cat = scene.get("category", "General")
            cat_data = CATEGORIES.get(cat, CATEGORIES["General"])
            status = scene.get("status", "draft")
            status_data = SCENE_STATUS.get(status, SCENE_STATUS["draft"])
            wc = len(scene.get("text", "").split()) if scene.get("text", "").strip() else 0
            
            prefix = ""
            if scene_id in bm: prefix += "⭐ "
            if scene.get("locked"): prefix += "🔒 "
            prefix += status_data["icon"] + " "
            
            display = f"{prefix}{cat_data['icon']} {scene['title']}\n    {wc}w • {calc_reading_time(scene.get('text',''))}"
            
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, scene_id)
            item.setForeground(QColor(cat_data["color"]))
            item.setSizeHint(QSize(0, 50))
            self.scene_list.addItem(item)
        
        if current_id:
            for i in range(self.scene_list.count()):
                item = self.scene_list.item(i)
                if item.data(Qt.UserRole) == current_id:
                    self.scene_list.blockSignals(True)
                    self.scene_list.setCurrentItem(item)
                    self.scene_list.blockSignals(False)
                    break
    
    def add_new_scene(self):
        self.push_undo()
        nid = f"scene_{uuid.uuid4().hex[:6]}"
        self.story_data["scenes"][nid] = {
            "title": "New Scene", "category": "General", "chapter": "", "status": "draft",
            "text": "", "transition": "fade", "effect": "none",
            "image": "", "notes": "", "bgm": "", "sfx": "",
            "requires_tags": "", "grants_tags": "",
            "variable_changes": "", "variable_conditions": "",
            "on_enter_script": "", "on_exit_script": "",
            "time_advance": 1, "map_marker": "",
            "todos": [], "dialogue": [], "combat": {}, "comments": [],
            "locked": False, "translations": {}, "options": []
        }
        self.refresh_scene_list()
        self.open_scene_tab(nid)
        self.mark_dirty()
    
    def quick_jump(self):
        scenes = list(self.story_data["scenes"].items())
        names = [f"{s['title']} ({sid})" for sid, s in scenes]
        name, ok = QInputDialog.getItem(self, "Quick Jump", "Select scene:", names, 0, False)
        if ok and name:
            idx = names.index(name)
            scene_id = scenes[idx][0]
            self.open_scene_tab(scene_id)
    
    def show_shortcuts(self):
        dlg = ShortcutsOverlay(self)
        dlg.exec()
    
    def save_story(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Story", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.get_story_data(), f, indent=2)
                QMessageBox.information(self, "Saved", f"Story saved to:\n{path}")
                self.autosave_dirty = False
                if self.window() and hasattr(self.window(), 'update_autosave_indicator'):
                    self.window().update_autosave_indicator(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def get_story_data(self):
        return self.story_data
    
    def set_story_data(self, data):
        for i in range(self.tab_widget.count() - 1, -1, -1):
            self.close_tab(i)
        
        for sid, sd in data.get("scenes", {}).items():
            sd.setdefault("status", "draft")
            sd.setdefault("todos", [])
            sd.setdefault("chapter", "")
            sd.setdefault("dialogue", [])
            sd.setdefault("combat", {})
            sd.setdefault("comments", [])
            for k, d in [("transition","fade"),("effect","none"),("notes",""),
                        ("requires_tags",""),("grants_tags",""),("variable_changes",""),
                        ("on_enter_script",""),("on_exit_script",""),("map_marker","")]:
                sd.setdefault(k, d)
            for opt in sd.get("options", []):
                for k, d in [("requires_tags",""),("grants_tags",""),("variable_changes",""),
                            ("skill_check",""),("success_target",""),("failure_target",""),
                            ("achievement",""),("sfx",""),("on_click_script",""),("translations",{})]:
                    opt.setdefault(k, d)
        
        data.setdefault("bookmarks", [])
        data.setdefault("templates", {})
        data.setdefault("variables", {})
        data.setdefault("inventory", {})
        data.setdefault("characters", {})
        data.setdefault("relationships", {})
        data.setdefault("quests", {})
        data.setdefault("chapters", {})
        data.setdefault("map_locations", {})
        data.setdefault("codex", {})
        data.setdefault("achievements", [])
        data.setdefault("ending_gallery", {})
        data.setdefault("version_snapshots", {})
        data.setdefault("time_system", {"enabled":False,"current_hour":8,"current_day":1})
        data.setdefault("languages", {"en":"English"})
        data.setdefault("current_language", "en")
        data.setdefault("word_goal", 5000)
        
        self.story_data = data
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.refresh_all()
        if self.story_data["scenes"]:
            self.open_scene_tab(self.story_data["start_scene"])

# =====================================================================
# MAIN WINDOW
# =====================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Adventure Story Creator Pro — Complete Edition")
        self.resize(1400, 900)
        self.editor = StoryEditor()
        self.setCentralWidget(self.editor)
        self.settings = QSettings("AdventureCreator", "StoryEditor")
        self.init_menu()
        self.init_statusbar()
        self.check_recovery()
    
    def init_menu(self):
        mb = self.menuBar()
        
        fm = mb.addMenu("File")
        save_a = QAction("💾 Save", self); save_a.setShortcut("Ctrl+S")
        save_a.triggered.connect(self.editor.save_story)
        fm.addAction(save_a)
        
        load_a = QAction("📂 Load", self); load_a.setShortcut("Ctrl+O")
        load_a.triggered.connect(self.load_story)
        fm.addAction(load_a)
        
        fm.addSeparator()
        
        export_menu = fm.addMenu("📤 Export")
        html_a = QAction("HTML5 Game", self); html_a.triggered.connect(lambda: self.export_story("html"))
        export_menu.addAction(html_a)
        md_a = QAction("Markdown", self); md_a.triggered.connect(lambda: self.export_story("md"))
        export_menu.addAction(md_a)
        txt_a = QAction("Plain Text", self); txt_a.triggered.connect(lambda: self.export_story("txt"))
        export_menu.addAction(txt_a)
        
        fm.addSeparator()
        exit_a = QAction("Exit", self); exit_a.triggered.connect(self.close)
        fm.addAction(exit_a)
        
        em = mb.addMenu("Edit")
        undo_a = QAction("↶ Undo", self); undo_a.setShortcut("Ctrl+Z")
        undo_a.triggered.connect(self.editor.undo)
        em.addAction(undo_a)
        
        redo_a = QAction("↷ Redo", self); redo_a.setShortcut("Ctrl+Shift+Z")
        redo_a.triggered.connect(self.editor.redo)
        em.addAction(redo_a)
        
        vm = mb.addMenu("View")
        theme_menu = vm.addMenu("🎨 Theme")
        for theme_name in THEMES.keys():
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, t=theme_name: self.apply_theme(t))
            theme_menu.addAction(action)
        
        hm = mb.addMenu("Help")
        shortcuts_a = QAction("⌨️ Keyboard Shortcuts", self); shortcuts_a.setShortcut("F1")
        shortcuts_a.triggered.connect(self.editor.show_shortcuts)
        hm.addAction(shortcuts_a)
        
        about_a = QAction("ℹ️ About", self); about_a.triggered.connect(self.show_about)
        hm.addAction(about_a)
    
    def init_statusbar(self):
        sb = self.statusBar()
        
        self.autosave_indicator = QLabel("●")
        self.autosave_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
        self.autosave_indicator.setToolTip("All changes saved")
        sb.addPermanentWidget(self.autosave_indicator)
        
        self.stats_label = QLabel()
        sb.addPermanentWidget(self.stats_label)
        self.update_stats()
    
    def update_autosave_indicator(self, saved):
        if saved:
            self.autosave_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
            self.autosave_indicator.setToolTip("All changes saved")
        else:
            self.autosave_indicator.setStyleSheet("color: #FF9800; font-size: 16px;")
            self.autosave_indicator.setToolTip("Unsaved changes")
    
    def update_stats(self):
        d = self.editor.get_story_data()
        sc = len(d["scenes"])
        wc = sum(len(s["text"].split()) for s in d["scenes"].values())
        rt = calc_reading_time(" ".join(s["text"] for s in d["scenes"].values()))
        self.stats_label.setText(f"📚 {sc} scenes • 📝 {wc} words • ⏱️ {rt}")
    
    def apply_theme(self, theme_name):
        if theme_name not in THEMES: theme_name = "Dark"
        theme = THEMES[theme_name]
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme["Window"]))
        palette.setColor(QPalette.WindowText, QColor(theme["WindowText"]))
        palette.setColor(QPalette.Base, QColor(theme["Base"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["AlternateBase"]))
        palette.setColor(QPalette.Text, QColor(theme["Text"]))
        palette.setColor(QPalette.Button, QColor(theme["Button"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["ButtonText"]))
        palette.setColor(QPalette.Highlight, QColor(theme["Highlight"]))
        palette.setColor(QPalette.HighlightedText, QColor(theme["HighlightedText"]))
        palette.setColor(QPalette.Link, QColor(theme["Link"]))
        palette.setColor(QPalette.PlaceholderText, QColor(theme["PlaceholderText"]))
        QApplication.setPalette(palette)
        self.settings.setValue("theme", theme_name)
    
    def check_recovery(self):
        autosave = self.settings.value("autosave")
        autosave_time = self.settings.value("autosave_time")
        if autosave and autosave_time:
            if QMessageBox.question(self, "Recovery",
                f"Found auto-save from {autosave_time}.\nRecover?") == QMessageBox.Yes:
                try:
                    data = json.loads(autosave)
                    self.editor.set_story_data(data)
                except: pass
    
    def load_story(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Story", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.editor.set_story_data(data)
                self.update_stats()
                QMessageBox.information(self, "Loaded", "Story loaded!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def export_story(self, format):
        data = self.editor.get_story_data()
        
        if format == "html":
            path, _ = QFileDialog.getSaveFileName(self, "Export HTML5", "", "HTML Files (*.html)")
            if path:
                try:
                    html = self.generate_html(data)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    QMessageBox.information(self, "Exported", f"Story exported to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
        
        elif format == "md":
            path, _ = QFileDialog.getSaveFileName(self, "Export Markdown", "", "Markdown Files (*.md)")
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(f"# {data.get('title', 'Untitled')}\n\n")
                        f.write(f"**Author:** {data.get('author', 'Unknown')}\n\n")
                        f.write(f"{data.get('description', '')}\n\n---\n\n")
                        for sid, s in data["scenes"].items():
                            f.write(f"## {s['title']}\n\n**Category:** {s.get('category','General')}\n\n")
                            f.write(f"{s['text']}\n\n")
                            if s.get("options"):
                                f.write("### Choices\n\n")
                                for o in s["options"]:
                                    f.write(f"- {o['text']} → `{o['target']}`\n")
                            f.write("\n---\n\n")
                    QMessageBox.information(self, "Exported", f"Exported to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
        
        elif format == "txt":
            path, _ = QFileDialog.getSaveFileName(self, "Export Text", "", "Text Files (*.txt)")
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(f"{data.get('title','')}\n{'='*60}\n\n")
                        for sid, s in data["scenes"].items():
                            f.write(f"[{s['title']}]\n{s['text']}\n\n")
                    QMessageBox.information(self, "Exported", f"Exported to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
    
    def generate_html(self, story_data):
        """Generate complete HTML5 game"""
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{story_data.get('title','Adventure')}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#1e1e1e,#2d2d2d);color:#e0e0e0;min-height:100vh}}
.container{{max-width:900px;margin:0 auto;padding:20px}}
header{{text-align:center;margin-bottom:30px}}
h1{{color:#4CAF50;font-size:2.5em;text-shadow:2px 2px 4px rgba(0,0,0,0.5)}}
.subtitle{{color:#aaa;font-size:1.1em}}
.scene-card{{background:rgba(255,255,255,0.05);border-radius:15px;padding:30px;margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid rgba(76,175,80,0.2)}}
.scene-title{{font-size:2em;color:#4CAF50;margin-bottom:20px;text-align:center}}
.scene-text{{font-size:1.2em;line-height:1.8;margin-bottom:30px;white-space:pre-wrap;min-height:100px}}
.choices{{display:flex;flex-direction:column;gap:12px;align-items:center}}
.choice-btn{{padding:18px 30px;font-size:1.1em;background:linear-gradient(135deg,#333,#444);color:#fff;border:2px solid #555;border-radius:10px;cursor:pointer;width:100%;max-width:500px;transition:all 0.3s}}
.choice-btn:hover{{border-color:#4CAF50;transform:translateY(-2px);box-shadow:0 6px 20px rgba(76,175,80,0.3)}}
.choice-btn.timed{{border-color:#FF9800}}
.choice-btn.skill-check{{border-color:#9C27B0}}
.timer-bar{{position:absolute;bottom:0;left:0;height:4px;background:#FF9800;transition:width 0.1s linear}}
.ending{{color:#f44336;font-size:1.8em;font-weight:bold;margin-top:30px;text-align:center}}
.restart-btn{{background:linear-gradient(135deg,#4CAF50,#45a049);border-color:#4CAF50}}
.controls{{display:flex;justify-content:center;gap:10px;margin-top:20px;flex-wrap:wrap}}
.control-btn{{padding:10px 18px;font-size:0.95em;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(76,175,80,0.3);border-radius:8px;cursor:pointer}}
.control-btn:hover{{border-color:#4CAF50}}
.variables{{display:flex;justify-content:center;gap:15px;margin-top:15px;flex-wrap:wrap}}
.variable{{padding:8px 16px;background:rgba(76,175,80,0.2);border:1px solid #4CAF50;border-radius:8px}}
.variable-name{{opacity:0.7;font-size:0.9em}}
.variable-value{{color:#4CAF50;font-weight:bold;font-size:1.2em}}
.progress-bar{{width:100%;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;margin-top:15px;overflow:hidden}}
.progress-fill{{height:100%;background:#4CAF50;transition:width 0.5s}}
.cursor{{animation:blink 0.7s infinite;color:#4CAF50}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.notification{{position:fixed;top:20px;right:20px;padding:15px 25px;background:#4CAF50;color:#000;border-radius:10px;animation:slideIn 0.5s ease-out;z-index:1000;font-weight:bold}}
@keyframes slideIn{{from{{transform:translateX(400px)}}to{{transform:translateX(0)}}}}
.scene-enter-fade{{animation:fadeIn 0.6s ease-in}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@media(max-width:768px){{.container{{padding:10px}}h1{{font-size:1.8em}}.scene-title{{font-size:1.5em}}.scene-text{{font-size:1em}}.choice-btn{{padding:15px 20px;font-size:1em}}}}
</style></head><body>
<div class="container">
<header><h1>{story_data.get('title','Adventure')}</h1><div class="subtitle">{story_data.get('description','')}</div></header>
<div id="content"></div>
<div class="variables" id="vars"></div>
<div class="progress-bar"><div class="progress-fill" id="pf" style="width:0%"></div></div>
<div class="controls">
<button class="control-btn" onclick="toggleMute()">🔊 Audio</button>
<button class="control-btn" onclick="toggleAch()">🏆 Achievements</button>
<button class="control-btn" onclick="toggleCodex()">📖 Codex</button>
<button class="control-btn" onclick="toggleQuests()">📜 Quests</button>
<button class="control-btn" onclick="toggleGallery()">🎬 Endings</button>
<button class="control-btn" onclick="showSave()">💾 Save</button>
</div></div>
<div id="notifs"></div>
<script>
const story = {json.dumps(story_data).replace("</script>","<\\/script>")};
let tags=new Set(),variables={{}},curScene="",achievements=new Set(),visited=new Set(),codex=new Set(),endings=new Set(),quests={{}};
let bgm=new Audio();bgm.loop=true;let curBGM="",vol=0.5,muted=false,twTimer=null,fullTxt="",cIdx=0;
let pd=JSON.parse(localStorage.getItem('adv_p')||'{{"a":[],"c":[],"e":[]}}');
achievements=new Set(pd.a||[]);codex=new Set(pd.c||[]);endings=new Set(pd.e||[]);

function initVars(){{for(let k in story.variables)variables[k]={{value:story.variables[k].default,min:story.variables[k].min||0,max:story.variables[k].max||9999}}}}
function initQuests(){{for(let k in story.quests)quests[k]=JSON.parse(JSON.stringify(story.quests[k]))}}
function updVars(){{let h='';for(let k in variables)h+=`<div class="variable"><div class="variable-name">${{k}}</div><div class="variable-value">${{variables[k].value}}</div></div>`;document.getElementById('vars').innerHTML=h}}
function playBGM(s){{if(!s){{bgm.pause();curBGM="";return}}if(curBGM!==s){{bgm.src=s;bgm.volume=vol;bgm.play().catch(()=>{{}});curBGM=s}}}}
function playSFX(s){{if(!s||muted)return;let a=new Audio(s);a.volume=vol;a.play().catch(()=>{{}})}}
function toggleMute(){{muted=!muted;bgm.muted=muted}}
function chkTags(r){{if(!r)return true;return r.split(',').map(t=>t.trim().toLowerCase()).filter(t=>t).every(t=>t.startsWith('!')?!tags.has(t.substring(1)):tags.has(t))}}
function appTags(g){{if(!g)return;g.split(',').map(t=>t.trim().toLowerCase()).filter(t=>t).forEach(t=>{{if(t.startsWith('-'))tags.delete(t.substring(1));else tags.add(t)}})}}
function chkVC(c){{if(!c)return true;return c.split(',').map(x=>x.trim()).filter(x=>x).every(cond=>{{for(let op of ['>=','<=','!=','>','<','=']){{if(cond.includes(op)){{let p=cond.split(op);if(p.length===2){{let v=p[0].trim(),val=parseInt(p[1].trim());if(variables[v]){{let cur=variables[v].value;if(op==='>'&&!(cur>val))return false;if(op==='<'&&!(cur<val))return false;if(op==='>='&&!(cur>=val))return false;if(op==='<='&&!(cur<=val))return false;if(op==='='&&!(cur===val))return false;if(op==='!='&&!(cur!==val))return false}}}}break}}}}return true}})}}
function appVC(c){{if(!c)return;c.split(',').map(x=>x.trim()).filter(x=>x).forEach(ch=>{{for(let op of ['+','-','*','/']){{if(ch.includes(op)){{let p=ch.split(op);if(p.length===2){{let v=p[0].trim(),val=parseInt(p[1].trim());if(variables[v]){{let cur=variables[v].value;if(op==='+')cur+=val;if(op==='-')cur-=val;if(op==='*')cur*=val;if(op==='/')cur=val?Math.floor(cur/val):cur;cur=Math.max(variables[v].min,Math.min(variables[v].max,cur));variables[v].value=cur}}}}break}}}}}});updVars()}}
function procCond(text){{return text.replace(/\\{{if\\s+([^}}]+)\\}}(.*?)\\{{endif\\}}/gs,(m,c,ct)=>(chkTags(c)||chkVC(c))?ct:'')}}
function subV(text){{return text.replace(/\\{{(\\w+)\\}}/g,(m,v)=>variables[v]?variables[v].value:m)}}
function notify(msg){{const n=document.createElement('div');n.className='notification';n.textContent=msg;document.getElementById('notifs').appendChild(n);setTimeout(()=>n.remove(),3000)}}
function unlockAch(id){{if(!id||achievements.has(id))return;achievements.add(id);pd.a=[...achievements];localStorage.setItem('adv_p',JSON.stringify(pd));const a=story.achievements.find(x=>x.id===id);if(a)notify(`🏆 ${{a.icon}} ${{a.name}}`)}}
function unlockEnding(id,title){{if(!id||endings.has(id))return;endings.add(id);pd.e=[...endings];localStorage.setItem('adv_p',JSON.stringify(pd));notify(`🎬 Ending unlocked: ${{title||id}}`)}}
function chkCodex(){{for(let id in story.codex){{const e=story.codex[id];if(!codex.has(id)&&chkTags(e.unlock_tag||'')){{codex.add(id);pd.c=[...codex];localStorage.setItem('adv_p',JSON.stringify(pd));notify(`📖 ${{e.name}}`)}}}}}}
function chkQuestCompletion(){{for(let k in quests){{if(!quests[k].completed&&quests[k].completion_tags){{if(chkTags(quests[k].completion_tags)){{quests[k].completed=true;notify(`✅ Quest complete: ${{quests[k].name}}`)}}}}}}}}
function toggleCodex(){{const p=document.createElement('div');p.style.cssText='position:fixed;right:0;top:0;width:350px;height:100vh;background:rgba(0,0,0,0.95);padding:20px;overflow-y:auto;z-index:99;border-left:2px solid #4CAF50';let h='<h3 style="color:#4CAF50">📖 Codex</h3>';for(let id in story.codex){{const e=story.codex[id];const u=codex.has(id);h+=`<div style="padding:12px;margin-bottom:10px;background:rgba(255,255,255,0.05);border-radius:8px;border-left:3px solid #4CAF50;${{u?'':'opacity:0.4;filter:grayscale(1)'}}"><h4 style="color:#4CAF50">${{e.icon||'📜'}} ${{e.name}}</h4>${{u?`<p>${{e.text}}</p>`:'<p><em>???</em></p>'}}</div>`}}p.innerHTML=h;document.body.appendChild(p);p.onclick=()=>p.remove()}}
function toggleAch(){{const p=document.createElement('div');p.style.cssText='position:fixed;right:0;top:0;width:350px;height:100vh;background:rgba(0,0,0,0.95);padding:20px;overflow-y:auto;z-index:99;border-left:2px solid #4CAF50';let h='<h3 style="color:#4CAF50">🏆 Achievements</h3>';story.achievements.forEach(a=>{{const u=achievements.has(a.id);h+=`<div style="padding:12px;margin-bottom:10px;background:rgba(255,255,255,0.05);border-radius:8px;border-left:3px solid #4CAF50;${{u?'':'opacity:0.4;filter:grayscale(1)'}}"><h4 style="color:#4CAF50">${{a.icon}} ${{a.name}}</h4><p>${{a.description}}</p></div>`}});p.innerHTML=h;document.body.appendChild(p);p.onclick=()=>p.remove()}}
function toggleQuests(){{const p=document.createElement('div');p.style.cssText='position:fixed;right:0;top:0;width:350px;height:100vh;background:rgba(0,0,0,0.95);padding:20px;overflow-y:auto;z-index:99;border-left:2px solid #4CAF50';let h='<h3 style="color:#4CAF50">📜 Quests</h3>';for(let k in quests){{const q=quests[k];h+=`<div style="padding:12px;margin-bottom:10px;background:rgba(255,255,255,0.05);border-radius:8px;border-left:3px solid #4CAF50"><h4 style="color:#4CAF50">${{q.completed?'✅':'📜'}} ${{q.name}}</h4><p style="font-size:0.9em;opacity:0.8">${{q.description}}</p></div>`}}p.innerHTML=h;document.body.appendChild(p);p.onclick=()=>p.remove()}}
function toggleGallery(){{const p=document.createElement('div');p.style.cssText='position:fixed;right:0;top:0;width:350px;height:100vh;background:rgba(0,0,0,0.95);padding:20px;overflow-y:auto;z-index:99;border-left:2px solid #4CAF50';let h='<h3 style="color:#4CAF50">🎬 Ending Gallery</h3>';const allEndings=[];for(let sid in story.scenes){{const s=story.scenes[sid];if(s.ending_id)allEndings.push({{id:s.ending_id,title:s.ending_title||s.title}})}}allEndings.forEach(e=>{{const u=endings.has(e.id);h+=`<div style="padding:12px;margin-bottom:10px;background:rgba(255,255,255,0.05);border-radius:8px;border-left:3px solid #4CAF50;${{u?'':'opacity:0.4;filter:grayscale(1)'}}"><h4 style="color:#4CAF50">${{u?'🎬':'🔒'}} ${{u?e.title:'???'}}</h4></div>`}});p.innerHTML=h;document.body.appendChild(p);p.onclick=()=>p.remove()}}
function startTW(text,el){{clearInterval(twTimer);fullTxt=text;cIdx=0;el.innerHTML='<span class="cursor">▌</span>';twTimer=setInterval(()=>{{if(cIdx<fullTxt.length){{cIdx++;el.innerHTML=fullTxt.substring(0,cIdx).replace(/\\n/g,'<br>')+'<span class="cursor">▌</span>'}}else{{clearInterval(twTimer);el.innerHTML=fullTxt.replace(/\\n/g,'<br>')}}}},30)}}
function skipTW(el){{clearInterval(twTimer);el.innerHTML=fullTxt.replace(/\\n/g,'<br>')}}
function execScript(s){{if(!s)return;try{{const fn=new Function('tags','variables','notify','playScene',s);fn(tags,variables,notify,playScene)}}catch(e){{console.error(e)}}}}
function playScene(id){{
const prev=curScene;curScene=id;visited.add(id);const scene=story.scenes[id];if(!scene)return;
if(prev&&story.scenes[prev]&&story.scenes[prev].on_exit_script)execScript(story.scenes[prev].on_exit_script);
if(!chkTags(scene.requires_tags)||!chkVC(scene.variable_conditions)){{document.getElementById('content').innerHTML='<div class="scene-card"><p class="ending">Requirements not met.</p></div>';return}}
appTags(scene.grants_tags);appVC(scene.variable_changes);playBGM(scene.bgm);playSFX(scene.sfx);chkCodex();chkQuestCompletion();
if(scene.on_enter_script)execScript(scene.on_enter_script);
if(scene.ending_id)unlockEnding(scene.ending_id,scene.ending_title);
const tr=scene.transition||'fade';
let h=`<div class="scene-card scene-enter-${{tr}}"><h2 class="scene-title">${{scene.title}}</h2>`;
if(scene.image)h+=`<img src="${{scene.image}}" style="max-width:100%;max-height:400px;margin:20px auto;display:block;border-radius:10px;">`;
let txt=procCond(subV(scene.text));
h+=`<div class="scene-text" id="st" onclick="skipTW(this)"></div>`;
const opts=scene.options.filter(o=>chkTags(o.requires_tags)&&chkVC(o.variable_conditions));
if(!opts.length){{h+=`<p class="ending">The End</p><button class="choice-btn restart-btn" onclick="init()">🔄 Restart</button>`}}
else{{h+=`<div class="choices">`;opts.forEach((o,i)=>{{const tm=o.timer&&o.timer>0;h+=`<button class="choice-btn${{tm?' timed':''}}" onclick="choose('${{o.target}}','${{o.grants_tags}}','${{o.sfx}}','${{o.achievement||''}}','${{o.variable_changes}}','${{o.random_targets}}',${{o.timer||0}},'${{o.skill_check||''}}','${{o.success_target||''}}','${{o.failure_target||''}}')" data-key="${{i+1}}">${{i+1}}. ${{o.text}}${{tm?`<div class="timer-bar" id="tb_${{i}}"></div>`:''}}</button>`}});h+=`</div>`}}
h+=`</div>`;document.getElementById('content').innerHTML=h;startTW(txt,document.getElementById('st'));updVars();
document.getElementById('pf').style.width=(visited.size/Object.keys(story.scenes).length*100)+'%';
opts.forEach((o,i)=>{{if(o.timer&&o.timer>0){{let l=o.timer;const b=document.getElementById(`tb_${{i}}`);if(b){{const iv=setInterval(()=>{{l-=0.1;b.style.width=(l/o.timer*100)+'%';if(l<=0){{clearInterval(iv);choose(o.target,o.grants_tags,o.sfx,o.achievement||'',o.variable_changes,o.random_targets,0,'','','')}}}},100)}}}}}});
}}
function choose(tgt,g,sfx,ach,vc,rt,tm,sc,successT,failT){{
playSFX(sfx);appTags(g);appVC(vc);unlockAch(ach);
if(rt&&rt.length>0){{let ts=rt.split(',').map(t=>t.trim()).filter(t=>t);if(ts.length)tgt=ts[Math.floor(Math.random()*ts.length)]}}
playScene(tgt)}}
function showSave(){{let h='<div class="scene-card"><h3>💾 Save/Load</h3><div style="display:flex;gap:10px;flex-wrap:wrap">';for(let i=1;i<=3;i++){{const s=localStorage.getItem(`as_${{i}}`);h+=`<button class="control-btn" onclick="sv(${{i}})">Save ${{i}}</button>`;if(s)h+=`<button class="control-btn" onclick="ld(${{i}})">Load ${{i}}</button>`}}h+='</div></div>';document.getElementById('content').innerHTML+=h}}
function sv(i){{localStorage.setItem(`as_${{i}}`,JSON.stringify({{s:curScene,t:[...tags],v:variables,vi:[...visited],q:quests}}));notify(`💾 Saved ${{i}}`)}}
function ld(i){{const d=JSON.parse(localStorage.getItem(`as_${{i}}`)||'null');if(!d){{notify('❌ No save');return}}tags=new Set(d.t);variables=d.v||{{}};visited=new Set(d.vi||[]);quests=d.q||{{}};playScene(d.s);notify(`📂 Loaded ${{i}}`)}}
function init(){{tags.clear();visited.clear();initVars();initQuests();playScene(story.start_scene)}}
document.addEventListener('keydown',e=>{{if(e.key===' '){{e.preventDefault();let s=document.getElementById('st');if(s)skipTW(s)}}if(e.key>='1'&&e.key<='9'){{let b=document.querySelector(`[data-key="${{e.key}}"]`);if(b)b.click()}}}});
init();
</script></body></html>"""
    
    def show_about(self):
        QMessageBox.about(self, "About",
            "<h2>🎮 Adventure Story Creator Pro</h2>"
            "<p><b>Complete Edition</b></p>"
            "<p>A professional tool for creating interactive fiction and adventure games.</p>"
            "<p>Press F1 for keyboard shortcuts.</p>")

# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    theme = THEMES["Dark"]
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(theme["Window"]))
    palette.setColor(QPalette.WindowText, QColor(theme["WindowText"]))
    palette.setColor(QPalette.Base, QColor(theme["Base"]))
    palette.setColor(QPalette.AlternateBase, QColor(theme["AlternateBase"]))
    palette.setColor(QPalette.Text, QColor(theme["Text"]))
    palette.setColor(QPalette.Button, QColor(theme["Button"]))
    palette.setColor(QPalette.ButtonText, QColor(theme["ButtonText"]))
    palette.setColor(QPalette.Highlight, QColor(theme["Highlight"]))
    palette.setColor(QPalette.HighlightedText, QColor(theme["HighlightedText"]))
    palette.setColor(QPalette.Link, QColor(theme["Link"]))
    palette.setColor(QPalette.PlaceholderText, QColor(theme["PlaceholderText"]))
    app.setPalette(palette)
    
    app.setStyleSheet("""
        QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 5px; margin-top: 10px; padding-top: 10px; }
        QPushButton { background-color: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 6px 14px; color: #ccc; }
        QPushButton:hover { background-color: #4a4a4a; border-color: #4CAF50; }
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox { border: 1px solid #444; border-radius: 4px; padding: 5px; background-color: #252526; color: #d4d4d4; }
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border-color: #4CAF50; }
        QTabWidget::pane { border: 1px solid #444; background: #1e1e1e; }
        QTabBar::tab { background: #2d2d30; border: 1px solid #444; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #ccc; }
        QTabBar::tab:selected { background: #1e1e1e; border-bottom: 2px solid #4CAF50; color: white; }
        QListWidget { background-color: #252526; border: 1px solid #444; border-radius: 4px; color: #d4d4d4; }
        QListWidget::item:selected { background-color: #264f78; }
        QMenuBar { background-color: #2d2d30; color: #ccc; }
        QMenuBar::item:selected { background-color: #4CAF50; color: white; }
        QMenu { background-color: #2d2d30; color: #ccc; border: 1px solid #444; }
        QMenu::item:selected { background-color: #4CAF50; color: white; }
        QStatusBar { background-color: #007acc; color: white; }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
