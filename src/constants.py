"""Application-wide constants"""

# ── File paths ────────────────────────────────────────────────────────────────
PROJECTS_FILE     = "data/Project.json"
ASSETS_SHOTS_FILE = "data/production.json"

# ── App window ────────────────────────────────────────────────────────────────
APP_TITLE     = "VFX Pipeline Production Tool"
WINDOW_WIDTH  = 1200
WINDOW_HEIGHT = 900

# ── Date format ───────────────────────────────────────────────────────────────
DATE_FORMAT = "%Y-%m-%d"

# ── Domain lists ──────────────────────────────────────────────────────────────
DEPARTMENTS   = ["Rig", "FX", "Animation", "Assets"]
PROJECT_TYPES = ["Animation", "VFX", "Gaming"]

# ── Model defaults ────────────────────────────────────────────────────────────
DEFAULT_DEPARTMENT       = "Rig"
DEFAULT_PROJECT_TYPE     = "VFX"
DEFAULT_TASK_STATUS      = "pending"
DEFAULT_TASK_PRIORITY    = "medium"
DEFAULT_ASSET_TYPE       = "model"
DEFAULT_SHOT_DEPARTMENT  = "FX"
DEFAULT_SHOT_STATUS      = "Pending"
DEFAULT_PRIORITY         = 50
DEFAULT_TIMELINE_OFFSET  = 25
DEFAULT_COMPLETION       = 25

# ── Assets tab ────────────────────────────────────────────────────────────────
SHOT_HEADERS = ["Shot", "Department", "Status", "Due Date"]

DEPARTMENT_TREE = {
    "Rig": {
        "Lead":  ["Senior Rigger", "Junior Rigger"],
        "Tools": ["Pipeline TD", "Tech Animator"],
    },
    "FX": {
        "Simulation": ["Houdini Artist", "FX TD"],
        "Rendering":  ["Lighting TD", "Comp Artist"],
    },
    "Animation": {
        "Character": ["Lead Animator", "Animator"],
        "Crowd":     ["Crowd TD", "Animator"],
    },
    "Assets": {
        "Modeling":  ["Lead Modeler", "Modeler"],
        "Texturing": ["Lead Texture", "Texture Artist"],
    },
}

# ── Default seed data ─────────────────────────────────────────────────────────
DEFAULT_SHOTS = [
    {"id": "shot_001", "shot": "SH010", "department": "FX",        "status": "In Progress", "due_date": "2026-06-15"},
    {"id": "shot_002", "shot": "SH020", "department": "Rig",        "status": "Pending",     "due_date": "2026-06-20"},
    {"id": "shot_003", "shot": "SH030", "department": "Animation",  "status": "Done",        "due_date": "2026-05-30"},
    {"id": "shot_004", "shot": "SH040", "department": "Assets",     "status": "Pending",     "due_date": "2026-07-01"},
    {"id": "shot_005", "shot": "SH050", "department": "FX",         "status": "In Progress", "due_date": "2026-06-28"},
    {"id": "shot_006", "shot": "SH060", "department": "Animation",  "status": "Pending",     "due_date": "2026-07-10"},
    {"id": "shot_007", "shot": "SH070", "department": "Rig",        "status": "Done",        "due_date": "2026-05-25"},
]
