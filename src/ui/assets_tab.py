"""Assets tab - Published Assets, Shot Tracking, Department Hierarchy"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView, QPushButton
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

from src.data_manager import DataManager
from src.constants import SHOT_HEADERS, DEPARTMENT_TREE


class AssetsTab(QWidget):
    """Tab with three panels: Published Assets, Shot Tracking, Department Hierarchy"""

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.init_ui()
        self._connect_signals()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # ── Panel 1 — Published Assets ────────────────────────────────────
        assets_group = QGroupBox("Published Assets")
        assets_layout = QVBoxLayout()

        self.asset_list = QListWidget()
        self.asset_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        assets_layout.addWidget(self.asset_list)
        assets_group.setLayout(assets_layout)

        # ── Panel 2 — Shot Tracking ───────────────────────────────────────
        shots_group = QGroupBox("Shot Tracking")
        shots_layout = QVBoxLayout()

        self.shot_table = QTableWidget()
        self.shot_table.setColumnCount(len(SHOT_HEADERS))
        self.shot_table.setHorizontalHeaderLabels(SHOT_HEADERS)
        self.shot_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shot_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shot_table.setAlternatingRowColors(True)
        self.shot_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.shot_table.verticalHeader().setVisible(False)
        shots_layout.addWidget(self.shot_table)
        shots_group.setLayout(shots_layout)

        # ── Panel 3 — Department Hierarchy ────────────────────────────────
        dept_group = QGroupBox("Department Hierarchy")
        dept_layout = QVBoxLayout()

        tree_toolbar = QHBoxLayout()
        self.tree_toggle_btn = QPushButton("Collapse All")
        self.tree_toggle_btn.setCheckable(True)
        self.tree_toggle_btn.setChecked(True)
        self.tree_toggle_btn.setFixedHeight(36)
        self.tree_toggle_btn.setMinimumWidth(120)
        self.tree_toggle_btn.toggled.connect(self._on_tree_toggle)
        tree_toolbar.addStretch()
        tree_toolbar.addWidget(self.tree_toggle_btn)
        dept_layout.addLayout(tree_toolbar)

        self.dept_tree = QTreeWidget()
        self.dept_tree.setHeaderLabel("Pipeline Departments")
        self.dept_tree.setAnimated(True)
        self.dept_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._populate_department_tree()
        dept_layout.addWidget(self.dept_tree)
        dept_group.setLayout(dept_layout)

        splitter.addWidget(assets_group)
        splitter.addWidget(shots_group)
        splitter.addWidget(dept_group)
        splitter.setSizes([100, 420, 300])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _connect_signals(self):
        self.asset_list.currentItemChanged.connect(self._on_asset_selected)
        self.shot_table.itemSelectionChanged.connect(self._on_shot_selected)

    def _on_asset_selected(self, current, previous):
        if not current:
            if self.parent_window:
                self.parent_window.statusBar().clearMessage()
            return
        if self.parent_window:
            self.parent_window.statusBar().showMessage(f"Asset:  {current.text()}")

    def _on_shot_selected(self):
        row = self.shot_table.currentRow()
        if row < 0:
            if self.parent_window:
                self.parent_window.statusBar().clearMessage()
            return
        shot   = self.shot_table.item(row, 0).text()
        dept   = self.shot_table.item(row, 1).text()
        status = self.shot_table.item(row, 2).text()
        due    = self.shot_table.item(row, 3).text()
        if self.parent_window:
            self.parent_window.statusBar().showMessage(
                f"Shot: {shot}  |  Dept: {dept}  |  Status: {status}  |  Due: {due}"
            )

    def _on_tree_toggle(self, checked: bool):
        if checked:
            self.dept_tree.expandAll()
            self.tree_toggle_btn.setText("Collapse All")
        else:
            self.dept_tree.collapseAll()
            self.tree_toggle_btn.setText("Expand All")

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
        # Assets
        self.asset_list.clear()
        for asset in self.data_manager.get_all_assets():
            item = QListWidgetItem(f"{asset.name}  [{asset.asset_type}]")
            item.setData(Qt.UserRole, asset.id)
            self.asset_list.addItem(item)

        # Shots
        shots = self.data_manager.get_all_shots()
        self.shot_table.setRowCount(len(shots))
        for row, shot in enumerate(shots):
            self.shot_table.setItem(row, 0, QTableWidgetItem(shot.shot))
            self.shot_table.setItem(row, 1, QTableWidgetItem(shot.department))
            self.shot_table.setItem(row, 2, QTableWidgetItem(shot.status))
            self.shot_table.setItem(row, 3, QTableWidgetItem(shot.due_date))
            bg = QColor("#2d6a2d") if shot.status.lower() == "done" else QColor("#6a2d2d")
            fg = QColor("#c8f0c8") if shot.status.lower() == "done" else QColor("#f0c8c8")
            for col in range(4):
                item = self.shot_table.item(row, col)
                item.setBackground(bg)
                item.setForeground(fg)
