# VFX Pipeline Production Tool

A modular PySide2 desktop application for managing VFX projects, tasks, shot tracking, and assets and full JSON persistence.

---

## Features

### Tab 1 — Planner
- Create, edit, and delete **projects** with name, supervisor, department, and project type (Animation / VFX / Gaming)
- Set project **flags**: Needs Daily Review, Client Delivery, High Priority
- **Priority slider** — auto-saves on release
- **Timeline Offset scrollbar** — auto-saves on release
- **Completion slider + progress bar**:
  - Sliding to 100% marks all tasks as **Done** automatically
  - Sliding back below 100% restores each task's previous status
- **Add / Remove tasks** per project
- **Mark Done** for individual tasks
- **Project Notes** text area with Clear Notes action
- **Save Changes** button for bulk field updates
- Formatted task list: `ProjectName  |  Department  |  TaskName  |  status`

### Tab 2 — Assets
- **Published Assets** panel — lists all assets stored in JSON
- **Shot Tracking** table — Shot, Department, Status, Due Date; fully persisted in JSON alongside projects and assets
- **Department Hierarchy** tree — Pipeline department / sub-group / role structure
  - Toggle button to **Collapse All / Expand All** the entire tree

### Tab 3 — Summary
- Live statistics: total projects, tasks by status (pending / in-progress / done), total assets
- **Export Summary as JSON** — saves a full snapshot of projects, tasks, assets, and statistics to a user-chosen file

### Menu Bar
| Menu | Action | Shortcut |
|------|--------|----------|
| File | New Project | Ctrl+N |
| File | Open Project… | Ctrl+O |
| File | Save Project… | Ctrl+S |
| File | Exit | Ctrl+Q |
| Help | About | F1 |

### UI Theme
Dark ink-wash palette applied via `resources/style.qss` — charcoal black, cool gray, and soft ivory for a gallery-like, high-contrast feel.

---

## Project Structure

```
Pipeline-Production-Tool/
├── main.py                        # Entry point
├── requirements.txt               # Python dependencies
├── README.md
├── resources/
│   └── style.qss                  # App-wide dark ink-wash stylesheet
├── data/
│   └── pipeline_data.json         # Persistent JSON storage (auto-created)
└── src/
    ├── app.py                     # App init — loads stylesheet, launches window
    ├── data_manager.py            # JSON persistence layer (projects, tasks, assets, shots)
    ├── models/
    │   ├── data_models.py         # Dataclasses: Project, Task, Asset, Shot
    │   └── asset_models.py        # Qt models: AssetListModel, ShotTableModel, DEPARTMENT_TREE
    └── ui/
        ├── main_window.py         # Main window — tab widget, menu bar, file I/O
        ├── planner_tab.py         # Tab 1 — project/task management
        ├── assets_tab.py          # Tab 2 — assets, shot tracking, dept hierarchy
        └── summary_tab.py         # Tab 3 — statistics, export
```

---

## Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd Pipeline-Production-Tool

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

---

## Data Storage

All data is stored in `data/pipeline_data.json`, created automatically on first run. Shot tracking is seeded with 7 default shots on first launch; any edits persist across restarts.

```json
{
  "projects": [
    {
      "id": "proj_abc12345",
      "name": "Dragon FX",
      "supervisor_name": "Jane Smith",
      "department": "FX",
      "project_type": "VFX",
      "needs_daily_review": true,
      "client_delivery": false,
      "high_priority": true,
      "priority": 80,
      "timeline_offset": 30,
      "completion": 60,
      "notes": "Client review on Friday.",
      "created_date": "2026-05-28",
      "tasks": [
        {
          "id": "task_001",
          "name": "Simulate smoke",
          "status": "in-progress",
          "priority": "high",
          "created_date": "2026-05-28"
        }
      ]
    }
  ],
  "assets": [
    {
      "id": "asset_001",
      "name": "Dragon_Rig_v3",
      "type": "model",
      "created_date": "2026-05-28"
    }
  ],
  "shots": [
    {
      "id": "shot_001",
      "shot": "SH010",
      "department": "FX",
      "status": "In Progress",
      "due_date": "2026-06-15"
    }
  ]
}
```

### Task statuses
`pending` · `in-progress` · `done`

### Asset types
`model` · `texture` · `animation` · *(any custom string)*

### Shot statuses
`Pending` · `In Progress` · `Done`

---

## Usage Guide

### Planner Tab

1. Fill in project details on the left panel and click **New Project** to create one.
2. Select a project from the **Projects** list to load its details and tasks.
3. Use **Add Task** / **Remove Task** to manage the task queue.
4. Click **Mark Done** to complete a selected task individually.
5. Drag the **Completion** slider to 100 to mark all tasks done at once; drag back below 100 to restore their previous statuses.
6. Click **Save Changes** to persist any form edits (name, department, flags, notes).

### Assets Tab

- The **Published Assets** panel reflects assets in `pipeline_data.json`.
- The **Shot Tracking** table is fully persisted — any changes written back to JSON are reflected immediately on tab switch.
- Use the **Collapse All / Expand All** toggle to navigate the Department Hierarchy tree.

### Summary Tab

- Statistics update whenever you switch to this tab.
- Click **Export Summary as JSON** to save a full pipeline snapshot for reporting or handoff.

### File Menu

- **Open Project (Ctrl+O)** — loads any `pipeline_data.json` file and replaces the current session.
- **Save Project (Ctrl+S)** — writes the current session to a new JSON file of your choice.

---

## Dependencies

| Package | Version |
|---------|---------|
| PySide2 | 5.15.13 |

Python standard library only beyond PySide2 (`json`, `uuid`, `datetime`, `pathlib`).
