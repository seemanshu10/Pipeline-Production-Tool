# VFX Pipeline Production Tool

A modular PySide2 desktop application for managing VFX projects, tasks, and assets with persistent JSON storage.

## Features

- **Planner Tab**: Create and manage projects with task queues
- **Assets Tab**: Track VFX assets (models, textures, animations, etc.)
- **Summary Tab**: View project statistics and overview

## Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Project Structure

```
Pipeline-Production-Tool/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/
│   └── pipeline_data.json     # Persistent JSON storage (auto-created)
├── src/
│   ├── __init__.py
│   ├── app.py                 # Main application class
│   ├── data_manager.py        # JSON persistence layer
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py     # Data classes (Project, Task, Asset)
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py     # Main window with tabs
│       ├── planner_tab.py     # Planner tab UI
│       ├── assets_tab.py      # Assets tab UI
│       └── summary_tab.py     # Summary tab UI
```

## Data Storage

All data is stored in `data/pipeline_data.json` in the following format:

```json
{
  "projects": [
    {
      "id": "proj_001",
      "name": "Project Name",
      "created_date": "2026-05-28",
      "tasks": [
        {
          "id": "task_001",
          "name": "Task Name",
          "status": "pending",
          "priority": "medium",
          "created_date": "2026-05-28"
        }
      ]
    }
  ],
  "assets": [
    {
      "id": "asset_001",
      "name": "Asset Name",
      "type": "model",
      "created_date": "2026-05-28"
    }
  ]
}
```

## Usage

1. **Planner Tab**:
   - Create a new project using the "New Project" button
   - Select a project to view its tasks
   - Add tasks to projects using the "New Task" button
   - Delete projects or tasks as needed

2. **Assets Tab**:
   - Create new assets using the "New Asset" button
   - View all assets in a list
   - Delete assets as needed

3. **Summary Tab**:
   - View overall project statistics
   - See counts of projects, tasks, and assets

## Notes

- All changes are automatically saved to `data/pipeline_data.json`
- Data persists across application restarts
- This is an initial version with basic CRUD functionality

## Future Features

- Edit functionality for projects, tasks, and assets
- Advanced task management (dependencies, priorities, deadlines)
- Asset linking to tasks
- User management and team collaboration
- Export/reporting features
- Customizable UI themes
