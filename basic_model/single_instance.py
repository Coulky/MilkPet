# -*- coding: utf-8 -*-
"""
单实例检测模块

使用文件锁方式实现单实例检测，避免 ctypes.wintypes 导致的编码问题
"""

import os
import sys
import tempfile
from pathlib import Path


class SingleInstanceChecker:
    """
    单实例检测器
    
    使用文件锁机制确保同一时间只有一个实例运行
    """
    
    def __init__(self, app_name="MilkPet"):
        """
        初始化单实例检测器
        
        参数:
            app_name: 应用程序名称（用于生成唯一的锁文件名）
        """
        self.app_name = app_name
        self.lock_file_path = None
        self.lock_file_handle = None
        self._is_running = False
    
    def is_already_running(self):
        """
        检查是否已有实例在运行
        
        返回:
            bool: True 表示已有实例运行，False 表示可以启动新实例
        """
        try:
            # 获取临时目录
            temp_dir = Path(tempfile.gettempdir())
            
            # 生成唯一的锁文件路径
            lock_file_name = f"{self.app_name}_instance.lock"
            self.lock_file_path = temp_dir / lock_file_name
            
            # 尝试创建并锁定文件
            if sys.platform == 'win32':
                # Windows 平台使用 msvcrt 进行文件锁定
                import msvcrt
                
                try:
                    # 以独占模式打开文件
                    self.lock_file_handle = open(str(self.lock_file_path), 'w')
                    
                    # 尝试获取文件锁（非阻塞模式）
                    msvcrt.locking(self.lock_file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                    
                    # 写入当前进程ID
                    self.lock_file_handle.write(str(os.getpid()))
                    self.lock_file_handle.flush()
                    
                    print(f"[OK] 单实例检查通过，进程 ID: {os.getpid()}")
                    return False
                    
                except (IOError, OSError):
                    # 文件已被锁定，说明已有实例运行
                    if self.lock_file_handle:
                        self.lock_file_handle.close()
                        self.lock_file_handle = None
                    
                    print("[WARN] 检测到已有实例正在运行")
                    return True
                    
            else:
                # Linux/Mac 使用 fcntl
                import fcntl
                
                try:
                    # 创建锁文件
                    self.lock_file_handle = open(str(self.lock_file_path), 'w')
                    
                    # 尝试获取排他锁（非阻塞）
                    fcntl.flock(self.lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    
                    # 写入PID
                    self.lock_file_handle.write(str(os.getpid()))
                    self.lock_file_handle.flush()
                    
                    print(f"[OK] 单实例检查通过，进程 ID: {os.getpid()}")
                    return False
                    
                except (IOError, OSError):
                    # 锁定失败，已有实例
                    if self.lock_file_handle:
                        self.lock_file_handle.close()
                        self.lock_file_handle = None
                    
                    print("[WARN] 检测到已有实例正在运行")
                    return True
                    
        except Exception as e:
            # 出现异常时允许启动（避免阻塞用户）
            print(f"[WARN] 单实例检查异常: {e}，允许启动")
            return False
    
    def release_lock(self):
        """
        释放文件锁
        """
        try:
            if self.lock_file_handle:
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(self.lock_file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                
                self.lock_file_handle.close()
                self.lock_file_handle = None
            
            # 删除锁文件
            if self.lock_file_path and os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
                
            print("[OK] 已释放单实例锁")
            
        except Exception as e:
            print(f"[WARN] 释放锁时出错: {e}")


def check_single_instance(app_name="MilkPet", show_message=True):
    """
    检查单实例的便捷函数
    
    参数:
        app_name: 应用名称
        show_message: 是否显示提示消息框（需要 PyQt5）
        
    返回:
        bool: True 表示可以继续运行，False 表示应退出
    """
    checker = SingleInstanceChecker(app_name)
    
    if checker.is_already_running():
        if show_message:
            try:
                from PyQt5.QtWidgets import QMessageBox, QApplication
                
                # 确保有 QApplication 实例
                app = QApplication.instance()
                if not app:
                    app = QApplication(sys.argv)
                
                # 显示系统提示窗口
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Milk Pet - 启动提示")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText("Milk Pet 已经在运行中！")
                msg_box.setInformativeText("请勿重复启动应用程序。")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setDefaultButton(QMessageBox.Ok)
                
                # 设置样式
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2b2b36;
                    }
                    QLabel {
                        color: #ffffff;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #5a7a9a;
                        color: white;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 4px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #6a8aaa;
                    }
                    QPushButton:pressed {
                        background-color: #4a6a8a;
                    }
                """)
                
                msg_box.exec_()
                
            except Exception as e:
                print(f"[ERROR] 显示提示框失败: {e}")
        
        return False
    
    # 存储检查器引用以便后续释放
    check_single_instance._checker = checker
    
    return True


def release_instance():
    """
    释放单实例锁（应在应用退出前调用）
    """
    if hasattr(check_single_instance, '_checker'):
        check_single_instance._checker.release_lock()