# -*- coding: utf-8 -*-
"""
桌宠显示模块 - 负责桌宠窗口的显示、图片加载和基础UI

独立模块：避免其他功能修改影响核心显示逻辑
"""

import sys
import os
import glob

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap


class PetDisplay(QWidget):
    """
    桌宠显示核心类
    
    职责：
    - 桌宠窗口创建和属性设置
    - 图片加载和显示
    - 动画帧播放支持
    - 基础UI布局
    """
    
    def __init__(self):
        super().__init__()
        
        self.pet_image_path = None
        self.pet_label = None
        
        # 动画相关
        self.animation_frames = []  # 存储所有动画帧的 QPixmap
        self.current_frame_index = 0  # 当前显示的帧索引
        self.animation_timer = QTimer(self)  # 动画播放定时器
        self.animation_timer.timeout.connect(self._next_frame)
        
        # 初始化显示
        self._load_pet_image()
        self._load_animation_frames()
        self._setup_window()
        self._setup_ui()
        self._move_to_bottom_right()
    
    def _find_resource_path(self, filename):
        """
        查找资源文件的路径
        
        参数:
            filename: 资源文件名（如 'milk.png', 'logo.png'）
            
        返回:
            str: 资源文件的完整路径，如果不存在则返回 None
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            # 获取项目根目录（向上两级：pet/pet_display.py -> pet/ -> 项目根）
            current_file = os.path.abspath(__file__)
            base_path = os.path.dirname(os.path.dirname(current_file))
        
        path = os.path.join(base_path, 'assets', 'images', filename)
        
        if os.path.exists(path):
            return path
        
        print(f"[WARN] 未找到资源文件: {filename}, 路径: {path}")
        return None
    
    def _load_pet_image(self):
        """加载桌宠图片"""
        self.pet_image_path = self._find_resource_path('milk.png')
        
        if self.pet_image_path:
            print(f"[OK] 找到桌宠图片: {self.pet_image_path}")
        else:
            print(f"[DEBUG] sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
    
    def _load_animation_frames(self):
        """加载动画帧图片（从 pet 文件夹加载所有 milk*.png）"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            current_file = os.path.abspath(__file__)
            base_path = os.path.dirname(os.path.dirname(current_file))
        
        pet_folder = os.path.join(base_path, 'assets', 'images', 'pet')
        
        if not os.path.exists(pet_folder):
            print(f"[WARN] 未找到 pet 动画文件夹: {pet_folder}")
            return
        
        # 查找所有 milk*.png 文件并排序
        pattern = os.path.join(pet_folder, 'milk*.png')
        frame_files = sorted(glob.glob(pattern))
        
        if not frame_files:
            print(f"[WARN] pet 文件夹中没有找到动画帧")
            return
        
        # 加载所有帧
        self.animation_frames = []
        for frame_file in frame_files:
            pixmap = QPixmap(frame_file)
            if not pixmap.isNull():
                self.animation_frames.append(pixmap)
        
        if self.animation_frames:
            print(f"[OK] 成功加载 {len(self.animation_frames)} 帧动画")
            # 默认显示第一帧
            self.current_frame_index = 0
            
            # 如果有动画帧，将默认图片路径设置为第一帧
            first_frame_path = frame_files[0] if frame_files else None
            if first_frame_path and os.path.exists(first_frame_path):
                self.pet_image_path = first_frame_path
                print(f"[OK] 使用动画第一帧作为默认图片: {first_frame_path}")
        else:
            print(f"[ERROR] 动画帧加载失败")
    
    def show_frame(self, index: int):
        """
        显示指定索引的动画帧
        
        参数：
            index: 帧索引
        """
        if not self.animation_frames or index >= len(self.animation_frames):
            return
        
        self.current_frame_index = index
        frame_pixmap = self.animation_frames[index]
        
        if self.pet_label and not frame_pixmap.isNull():
            # 使用与初始加载相同的缩放方式：保持比例，适应窗口大小
            scaled_pixmap = frame_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 设置固定尺寸的 pixmap，避免 QLabel 自动调整导致的大小变化
            self.pet_label.setFixedSize(scaled_pixmap.size())
            self.pet_label.setPixmap(scaled_pixmap)
    
    def play_animation(self, fps: int = 8, on_finished=None):
        """
        播放点击动画
        
        参数：
            fps: 每秒播放的帧数，默认为 8
            on_finished: 动画播放完成后的回调函数
        """
        if not self.animation_frames:
            print("[WARN] 没有可播放的动画帧")
            return
        
        # 停止当前正在播放的动画（如果有）
        self.stop_animation()
        
        # 从第 1 帧开始播放（跳过第 0 帧，因为第 0 帧是默认待机状态）
        self.current_frame_index = 0
        
        # 设置回调（如果提供）
        self._animation_callback = on_finished
        
        # 计算每帧间隔时间（毫秒）
        interval = 1000 // fps
        
        # 启动定时器
        self.animation_timer.start(interval)
        print(f"[ANIM] 开始播放动画，共 {len(self.animation_frames)} 帧，FPS: {fps}")
    
    def stop_animation(self):
        """停止动画播放"""
        self.animation_timer.stop()
    
    def _next_frame(self):
        """显示下一帧（由定时器调用）"""
        if not self.animation_frames:
            return
        
        # 移动到下一帧
        self.current_frame_index += 1
        
        # 如果到达最后一帧，停止动画并回到第一帧
        if self.current_frame_index >= len(self.animation_frames):
            self.stop_animation()
            
            # 回到第一帧（待机状态）
            self.show_frame(0)
            
            # 触发回调（如果存在）
            if hasattr(self, '_animation_callback') and self._animation_callback:
                callback = self._animation_callback
                self._animation_callback = None  # 清除回调防止重复调用
                callback()
            
            print("[ANIM] 动画播放完成")
            return
        
        # 显示当前帧
        self.show_frame(self.current_frame_index)
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Milk Pet")
        
        flags = (Qt.FramelessWindowHint | 
                Qt.WindowStaysOnTopHint | 
                Qt.Tool)
        self.setWindowFlags(flags)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        
        screen = QApplication.instance().primaryScreen().availableGeometry()
        max_size = min(screen.width() * 0.3, screen.height() * 0.4, 350)
        self.setFixedSize(int(max_size), int(max_size * 1.2))
    
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.pet_label = QLabel()
        self.pet_label.setAlignment(Qt.AlignCenter)
        
        if self.pet_image_path and os.path.exists(self.pet_image_path):
            pixmap = QPixmap(self.pet_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                # 设置固定尺寸，与动画帧显示保持一致
                self.pet_label.setFixedSize(scaled_pixmap.size())
                self.pet_label.setPixmap(scaled_pixmap)
                print("[OK] 桌宠图片加载成功")
            else:
                self.pet_label.setText("Milk")
                self.pet_label.setStyleSheet("font-size: 150px;")
                print("[WARN] 图片加载失败，使用占位符")
        else:
            self.pet_label.setText("Milk")
            self.pet_label.setStyleSheet("font-size: 150px;")
        
        layout.addWidget(self.pet_label)
        self.setLayout(layout)
    
    def _move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 40
        self.move(x, y)
    
    def get_logo_path(self):
        """获取logo图标路径"""
        return self._find_resource_path('logo.png')
    
    def update_pet_image(self, image_path=None):
        """
        更新桌宠图片
        
        参数:
            image_path: 新的图片路径，如果为None则重新加载默认图片
        """
        if not image_path:
            self._load_pet_image()
        else:
            if os.path.exists(image_path):
                self.pet_image_path = image_path
            else:
                print(f"[ERROR] 图片不存在: {image_path}")
                return
        
        if self.pet_label and self.pet_image_path and os.path.exists(self.pet_image_path):
            pixmap = QPixmap(self.pet_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pet_label.setPixmap(scaled_pixmap)
                print("[OK] 桌宠图片已更新")