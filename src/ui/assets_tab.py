"""Assets tab - Published Assets, Shot Tracking, Department Hierarchy"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QGroupBox,
    QListView, QTableView, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide2.QtCore import Qt

from src.data_manager import DataManager
from src.models.asset_models import AssetListModel, ShotTableModel, DEPARTMENT_TREE


class AssetsTab(QWidget):
    """Tab with three panels: Published Assets, Shot Tracking, Department Hierarchy"""

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.init_ui()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        # ------------------------------------------------------------------
        # Panel 1 — Published Assets
        # ------------------------------------------------------------------
        assets_group = QGroupBox("Published Assets")
        assets_layout = QVBoxLayout()

        self.asset_list_model = AssetListModel()
        self.asset_list_view = QListView()
        self.asset_list_view.setModel(self.asset_list_model)
        self.asset_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        assets_layout.addWidget(self.asset_list_view)
        assets_group.setLayout(assets_layout)

        # ------------------------------------------------------------------
        # Panel 2 — Shot Tracking
        # ------------------------------------------------------------------
        shots_group = QGroupBox("Shot Tracking")
        shots_layout = QVBoxLayout()

        self.shot_table_model = ShotTableModel()
        self.shot_table_view = QTableView()
        self.shot_table_view.setModel(self.shot_table_model)
        self.shot_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shot_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shot_table_view.setAlternatingRowColors(True)
        self.shot_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.shot_table_view.verticalHeader().setVisible(False)

        shots_layout.addWidget(self.shot_table_view)
        shots_group.setLayout(shots_layout)

        # ------------------------------------------------------------------
        # Panel 3 — Department Hierarchy
        # ------------------------------------------------------------------
        dept_group = QGroupBox("Department Hierarchy")
        dept_layout = QVBoxLayout()

        self.dept_tree = QTreeWidget()
        self.dept_tree.setHeaderLabel("Pipeline Departments")
        self.dept_tree.setAnimated(True)
        self.dept_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._populate_department_tree()

        dept_layout.addWidget(self.dept_tree)
        dept_group.setLayout(dept_layout)

        # ------------------------------------------------------------------
        # Assemble splitter
        # ------------------------------------------------------------------
        splitter.addWidget(assets_group)
        splitter.addWidget(shots_group)
        splitter.addWidget(dept_group)
        splitter.setSizes([280, 420, 300])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _populate_department_tree(self):
        self.dept_tree.clear()
        for dept, sub_groups in DEPARTMENT_TREE.items():
            dept_item = QTreeWidgetItem([dept])
            dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)
            for sub_group, roles in sub_groups.items():
                sub_item = QTreeWidgetItem([sub_group])
                sub_item.setFlags(sub_item.flags() & ~Qt.ItemIsEditable)
                for role in roles:
                    role_item = QTreeWidgetItem([role])
                    role_item.setFlags(role_item.flags() & ~Qt.ItemIsEditable)
                    sub_item.addChild(role_item)
                dept_item.addChild(sub_item)
            self.dept_tree.addTopLevelItem(dept_item)
        self.dept_tree.expandAll()

    def refresh(self):
        assets = self.data_manager.get_all_assets()
        self.asset_list_model.refresh(assets)
