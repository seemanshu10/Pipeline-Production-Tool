"""Assets tab - Asset management"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QInputDialog, QMessageBox, QComboBox
)
from PySide2.QtCore import Qt

from src.data_manager import DataManager


class AssetsTab(QWidget):
    """Tab for managing VFX assets"""
    
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.asset_types = ["model", "texture", "animation", "effect", "other"]
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Assets label and list
        layout.addWidget(QLabel("Assets:"))
        
        self.assets_list = QListWidget()
        layout.addWidget(self.assets_list)
        
        # Asset type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Asset Type:"))
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems(self.asset_types)
        type_layout.addWidget(self.asset_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        new_asset_btn = QPushButton("New Asset")
        new_asset_btn.clicked.connect(self.create_asset)
        delete_asset_btn = QPushButton("Delete Asset")
        delete_asset_btn.clicked.connect(self.delete_asset)
        btn_layout.addWidget(new_asset_btn)
        btn_layout.addWidget(delete_asset_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh assets list"""
        self.assets_list.clear()
        assets = self.data_manager.get_all_assets()
        
        for asset in assets:
            item_text = f"{asset.name} [{asset.asset_type}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, asset.id)
            self.assets_list.addItem(item)
    
    def create_asset(self):
        """Create a new asset"""
        name, ok = QInputDialog.getText(self, "New Asset", "Asset name:")
        if ok and name:
            asset_type = self.asset_type_combo.currentText()
            self.data_manager.create_asset(name, asset_type)
            self.refresh()
    
    def delete_asset(self):
        """Delete selected asset"""
        selected_items = self.assets_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an asset to delete.")
            return
        
        asset_id = selected_items[0].data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this asset?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_asset(asset_id)
            self.refresh()
