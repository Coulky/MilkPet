import sys
import os

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu,
                             QAction, QSystemTrayIcon, QVBoxLayout,
                             QHBoxLayout, QPushButton, QCheckBox)
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        
        self.dragging = False
        self.drag_position = QPoint()
        self.allow_click = True
        self.is_on_top = True
        
        self.pet_image_path = self._find_pet_image()
        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._move_to_bottom_right()
    
    def _find_pet_image(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "assets", "images", "yongbing.png"),
            os.path.join(base_dir, "yongbing.png"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None
    
    def _setup_window(self):
        self.setWindowTitle("桌面宠物")
        
        flags = (Qt.FramelessWindowHint | 
                Qt.WindowStaysOnTopHint | 
                Qt.Tool)
        self.setWindowFlags(flags)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        
        screen = QApplication.primaryScreen().availableGeometry()
        max_size = min(screen.width() * 0.3, screen.height() * 0.4, 350)
        self.setFixedSize(int(max_size), int(max_size * 1.2))
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignCenter)
        
        if self.pet_image_path and os.path.exists(self.pet_image_path):
            pixmap = QPixmap(self.pet_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pet_label.setPixmap(scaled_pixmap)
                print(f"✅ Pet image loaded: {self.pet_image_path}")
            else:
                self._show_placeholder()
        else:
            self._show_placeholder()
        
        self.pet_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.pet_label)
        
        self.menu_widget = QWidget(self)
        self.menu_widget.hide()
        self.menu_widget.setFixedSize(180, 280)
        self.menu_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 35, 0.95);
                border: 2px solid rgba(100, 100, 120, 1);
                border-radius: 12px;
            }
            QPushButton {
                background-color: rgba(50, 50, 60, 0.9);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 90, 0.95);
            }
            QPushButton:pressed {
                background-color: rgba(90, 90, 110, 0.95);
            }
            QCheckBox {
                color: rgb(220, 220, 220);
                font-size: 11px;
                padding: 6px;
            }
        """)
        
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(4)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_widget.setLayout(menu_layout)
        
        buttons = [
            ("🎒 背包", self._on_bag),
            ("🛒 商店", self._on_shop),
            ("⚙️ 设置", self._on_settings),
            ("ℹ️ 关于", self._on_about),
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            menu_layout.addWidget(btn)
        
        self.top_btn = QPushButton("📌 取消置顶")
        self.top_btn.clicked.connect(self._toggle_top)
        menu_layout.addWidget(self.top_btn)
        
        self.click_checkbox = QCheckBox("允许点击交互")
        self.click_checkbox.setChecked(True)
        self.click_checkbox.stateChanged.connect(self._on_click_toggle)
        menu_layout.addWidget(self.click_checkbox)
        
        menu_layout.addStretch()
    
    def _setup_tray(self):
        icon = QIcon(self.pet_image_path) if self.pet_image_path else QIcon()
        if icon.isNull():
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(100, 150, 255))
            icon = QIcon(pixmap)
        
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("桌面宠物 🐱")
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        tray_menu = QMenu()
        
        show_action = QAction("🐱 显示/隐藏", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        top_action = QAction("📌 取消置顶", self, checkable=True)
        top_action.setChecked(True)
        top_action.triggered.connect(lambda c: self._set_top(c))
        tray_menu.addAction(top_action)
        
        click_action = QAction("✅ 允许点击", self, checkable=True)
        click_action.setChecked(True)
        click_action.triggered.connect(lambda c: self._set_allow_click(c))
        tray_menu.addAction(click_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        print("✅ System tray icon created")
    
    def _move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 80
        self.move(x, y)
        print(f"📍 Position: ({x}, {y})")
    
    def _show_placeholder(self):
        self.pet_label.setText("🐱")
        self.pet_label.setStyleSheet("""
            font-size: 80px;
            background: transparent;
            color: rgba(255, 200, 100, 0.7);
        """)
        print("⚠️ Using placeholder emoji")
    
    def mousePressEvent(self, event):
        if not self.allow_click:
            event.ignore()
            return
            
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.menu_widget.hide()
            event.accept()
            
        elif event.button() == Qt.RightButton:
            self._toggle_menu(event.pos())
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def _toggle_menu(self, pos):
        if self.menu_widget.isVisible():
            self.menu_widget.hide()
        else:
            x = pos.x() + 20
            y = pos.y()
            if x + self.menu_widget.width() > self.width():
                x = pos.x() - self.menu_widget.width() - 20
            if y + self.menu_widget.height() > self.height():
                y = self.height() - self.menu_widget.height() - 10
            self.menu_widget.move(x, y)
            self.menu_widget.show()
            print("🖱️ Menu shown")
    
    def _on_bag(self):
        print("🎒 Bag clicked")
        self.menu_widget.hide()
        self.tray_icon.showMessage("背包", "功能开发中...", QSystemTrayIcon.Information, 2000)
    
    def _on_shop(self):
        print("🛒 Shop clicked")
        self.menu_widget.hide()
        self.tray_icon.showMessage("商店", "功能开发中...", QSystemTrayIcon.Information, 2000)
    
    def _on_settings(self):
        print("⚙️ Settings clicked")
        self.menu_widget.hide()
        self.tray_icon.showMessage("设置", "功能开发中...", QSystemTrayIcon.Information, 2000)
    
    def _on_about(self):
        print("ℹ️ About clicked")
        self.menu_widget.hide()
        self.tray_icon.showMessage(
            "关于",
            "桌面宠物 v1.0\n\n一个可爱的桌面伴侣 ✨",
            QSystemTrayIcon.Information,
            3000
        )
    
    def _toggle_top(self):
        self.is_on_top = not self.is_on_top
        self._update_window_flags()
        status = "开启" if self.is_on_top else "关闭"
        self.top_btn.setText(f"📌 {'取消置顶' if self.is_on_top else '置顶'}")
        print(f"📌 Top mode: {status}")
        self.tray_icon.showMessage("置顶", f"已{status}", QSystemTrayIcon.Information, 1500)
    
    def _set_top(self, enabled):
        self.is_on_top = enabled
        self._update_window_flags()
    
    def _on_click_toggle(self, state):
        self.allow_click = (state == Qt.Checked)
        if not self.allow_click:
            self.menu_widget.hide()
        status = "启用" if self.allow_click else "禁用"
        print(f"🖱️ Click interaction: {status}")
    
    def _set_allow_click(self, enabled):
        self.allow_click = enabled
        self.click_checkbox.setChecked(enabled)
    
    def _update_window_flags(self):
        flags = (Qt.FramelessWindowHint | 
                Qt.Tool |
                Qt.WindowTransparentForInput)
        if self.is_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
    
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
    
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
    
    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("桌面宠物")
    
    pet = DesktopPet()
    pet.show()
    
    print("\n" + "=" * 50)
    print("🐱 Desktop Pet Started!")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Right-click pet → Menu")
    print("   • Left-drag → Move")
    print("   • Double-click tray icon → Show/Hide")
    print("=" * 50 + "\n")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()