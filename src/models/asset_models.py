"""Qt models for the Assets tab views"""

from typing import List

from PySide2.QtCore import Qt, QAbstractListModel, QAbstractTableModel, QModelIndex

from src.models.data_models import Asset


# ---------------------------------------------------------------------------
# Shot tracking — sample data (no persistence layer yet)
# ---------------------------------------------------------------------------

SHOT_HEADERS = ["Shot", "Department", "Status", "Due Date"]

SAMPLE_SHOTS = [
    {"shot": "SH010", "department": "FX",        "status": "In Progress", "due_date": "2026-06-15"},
    {"shot": "SH020", "department": "Rig",        "status": "Pending",     "due_date": "2026-06-20"},
    {"shot": "SH030", "department": "Animation",  "status": "Done",        "due_date": "2026-05-30"},
    {"shot": "SH040", "department": "Assets",     "status": "Pending",     "due_date": "2026-07-01"},
    {"shot": "SH050", "department": "FX",         "status": "In Progress", "due_date": "2026-06-28"},
    {"shot": "SH060", "department": "Animation",  "status": "Pending",     "due_date": "2026-07-10"},
    {"shot": "SH070", "department": "Rig",        "status": "Done",        "due_date": "2026-05-25"},
]

# ---------------------------------------------------------------------------
# Department hierarchy — drives QTreeWidget population
# ---------------------------------------------------------------------------

# Structure: { Department: { SubGroup: [roles, ...], ... }, ... }
DEPARTMENT_TREE = {
    "Rig": {
        "Lead": ["Senior Rigger", "Junior Rigger"],
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


# ---------------------------------------------------------------------------
# AssetListModel — backs the Published Assets QListView
# ---------------------------------------------------------------------------

class AssetListModel(QAbstractListModel):
    """Read-only list model exposing Asset objects."""

    def __init__(self, assets: List[Asset] = None, parent=None):
        super().__init__(parent)
        self._assets: List[Asset] = assets or []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._assets)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._assets)):
            return None
        asset = self._assets[index.row()]
        if role == Qt.DisplayRole:
            return f"{asset.name}  [{asset.asset_type}]"
        if role == Qt.UserRole:
            return asset.id
        return None

    def refresh(self, assets: List[Asset]):
        self.beginResetModel()
        self._assets = assets
        self.endResetModel()


# ---------------------------------------------------------------------------
# ShotTableModel — backs the Shot Tracking QTableView (non-editable)
# ---------------------------------------------------------------------------

class ShotTableModel(QAbstractTableModel):
    """Read-only table model for shot tracking rows."""

    _KEYS = ["shot", "department", "status", "due_date"]

    def __init__(self, shots: List[dict] = None, parent=None):
        super().__init__(parent)
        self._shots: List[dict] = shots if shots is not None else SAMPLE_SHOTS

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._shots)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(SHOT_HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._shots)):
            return None
        if role == Qt.DisplayRole:
            return self._shots[index.row()][self._KEYS[index.column()]]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return SHOT_HEADERS[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
