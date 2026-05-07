import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QApplication, 
                             QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer

class PetCommunicator(QObject):
    pet_closed = pyqtSignal()

class DesktopPet:
    def __init__(self):
        self.pet_process = None
        self.tray_icon = None
        self.communicator = PetCommunicator()
        
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            self.app_dir = self.base_dir
        
        self.pet_exe = None
        self.icon_path = None
        
        self._find_icon()
        
    def _find_icon(self):
        candidates = [
            os.path.join(self.base_dir, "assets", "images", "yongbing.png"),
            os.path.join(self.app_dir, "assets", "images", "yongbing.png"),
            os.path.join(self.base_dir, "yongbing.png"),
            os.path.join(self.app_dir, "yongbing.png"),
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                self.icon_path = candidate
                break
        
    def _find_exe(self):
        candidates = [
            os.path.join(self.app_dir, "milk.exe"),
            os.path.join(self.app_dir, "DesktopPet.exe"),
            os.path.join(self.base_dir, "milk.exe"),
            os.path.join(os.path.dirname(self.app_dir), "ttt", "milk.exe"),
            os.path.join(self.app_dir, "..", "milk.exe"),
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
        
        return None
    
    def select_exe_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择桌宠程序",
            self.app_dir,
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        
        if file_path and os.path.exists(file_path):
            self.pet_exe = os.path.abspath(file_path)
            
            config_file = os.path.join(self.app_dir, "pet_config.txt")
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(f"exe_path={self.pet_exe}\n")
            except:
                pass
            
            print(f"✅ 已选择: {self.pet_exe}")
            return True
        
        return False
    
    def load_saved_config(self):
        config_file = os.path.join(self.app_dir, "pet_config.txt")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("exe_path=") and not line.startswith("#"):
                            path = line.split("=", 1)[1].strip()
                            if os.path.exists(path):
                                self.pet_exe = os.path.abspath(path)
                                print(f"📂 从配置加载: {self.pet_exe}")
                                return True
            except Exception as e:
                print(f"⚠️ 读取配置失败: {e}")
        
        return None
    
    def create_tray_icon(self):
        app = QApplication.instance()
        
        if not self.icon_path or not os.path.exists(self.icon_path):
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.blue)
            icon = QIcon(pixmap)
            print("⚠️ Using default icon")
        else:
            icon = QIcon(self.icon_path)
            print(f"✅ Icon loaded: {self.icon_path}")
        
        self.tray_icon = QSystemTrayIcon(icon)
        self.tray_icon.setToolTip("桌面宠物 🐱")
        
        menu = QMenu()
        
        show_action = QAction("🎒 背包", app)
        show_action.triggered.connect(lambda: self.show_message("背包功能开发中..."))
        menu.addAction(show_action)
        
        shop_action = QAction("🛒 商店", app)
        shop_action.triggered.connect(lambda: self.show_message("商店功能开发中..."))
        menu.addAction(shop_action)
        
        settings_action = QAction("⚙️ 设置", app)
        settings_action.triggered.connect(lambda: self.show_message("设置功能开发中..."))
        menu.addAction(settings_action)
        
        about_action = QAction("ℹ️ 关于", app)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        top_action = QAction("📌 取消置顶", app)
        top_action.setCheckable(True)
        top_action.setChecked(True)
        top_action.triggered.connect(lambda checked: self.toggle_top(checked))
        menu.addAction(top_action)
        
        click_action = QAction("✅ 允许点击交互", app)
        click_action.setCheckable(True)
        click_action.setChecked(True)
        click_action.triggered.connect(lambda checked: print(f"点击交互: {'启用' if checked else '禁用'}"))
        menu.addAction(click_action)
        
        menu.addSeparator()
        
        select_action = QAction("📂 选择程序...", app)
        select_action.triggered.connect(self.on_select_exe)
        menu.addAction(select_action)
        
        restart_action = QAction("🔄 重启桌宠", app)
        restart_action.triggered.connect(self.restart_pet)
        menu.addAction(restart_action)
        
        quit_action = QAction("❌ 退出", app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
        print("✅ System tray icon created!")
    
    def on_select_exe(self):
        if self.select_exe_file():
            self.show_message(f"已选择!\n{os.path.basename(self.pet_exe)}\n\n点击重启生效")
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.pet_process and self.pet_process.poll() is None:
                self.show_pet_window()
            else:
                self.start_pet()
    
    def start_pet(self):
        if self.pet_process and self.pet_process.poll() is None:
            return
        
        if not self.pet_exe or not os.path.exists(self.pet_exe):
            self.pet_exe = self._find_exe()
        
        if not self.pet_exe or not os.path.exists(self.pet_exe):
            print("\n❌ 找不到桌宠程序!")
            print("请右键托盘图标 → 选择程序...")
            
            QTimer.singleShot(1000, lambda: self.select_exe_file())
            return
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.pet_process = subprocess.Popen(
                [self.pet_exe],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            print(f"✅ Pet started! PID: {self.pet_process.pid}")
            self.show_message("桌面宠物已启动! 🐱")
            
            def monitor():
                if self.pet_process:
                    self.pet_process.wait()
                    print("⚠️ Pet process ended")
                    QTimer.singleShot(100, lambda: self.communicator.pet_closed.emit())
            
            monitor_thread = threading.Thread(target=monitor, daemon=True)
            monitor_thread.start()
            
        except Exception as e:
            self.show_message(f"❌ 启动失败: {str(e)}")
    
    def restart_pet(self):
        if self.pet_process and self.pet_process.poll() is None:
            self.pet_process.terminate()
            try:
                self.pet_process.wait(timeout=2)
            except:
                self.pet_process.kill()
        
        QTimer.singleShot(500, self.start_pet)
    
    def show_pet_window(self):
        pass
    
    def toggle_top(self, enabled):
        status = "开启" if enabled else "关闭"
        print(f"📌 置顶: {status}")
        self.show_message(f"置顶模式已{status}")
    
    def show_message(self, message):
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage("桌面宠物 🐱", message, QSystemTrayIcon.Information, 2000)
    
    def show_about(self):
        msg = """桌面宠物 v1.0

一个可爱的桌面宠物应用 ✨

功能：
• 拖拽移动到任意位置
• 右键弹出菜单
• 默认置顶显示
• 点击交互控制
• 系统托盘集成"""
        self.show_message(msg)
    
    def quit_app(self):
        print("👋 Quitting...")
        
        if self.pet_process and self.pet_process.poll() is None:
            self.pet_process.terminate()
            try:
                self.pet_process.wait(timeout=2)
            except:
                self.pet_process.kill()
        
        QApplication.instance().quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("桌面宠物")
    
    pet = DesktopPet()
    
    pet.load_saved_config()
    if not pet.pet_exe:
        pet.pet_exe = pet._find_exe()
    
    pet.create_tray_icon()
    QTimer.singleShot(1500, pet.start_pet)
    
    print("\n" + "="*50)
    print("🐱 桌面宠物系统托盘版 已启动!")
    print("="*50)
    print("💡 双击托盘图标或右键菜单操作")
    print("="*50 + "\n")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()