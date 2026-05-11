# -*- coding: utf-8 -*-
"""
Milk Pet 应用 - 主入口

模块说明：
- desktop_pet.py: 桌宠核心类（对应 scripts/games/PetMain.gd）
- games/dh_puzzle.py: 数字华容道游戏（使用 assets/images/sliding_puzzle/ 资源）
- games/sudoku.py: 数独游戏（使用 assets/images/sudoku/ 资源）

运行方式：
1. 直接运行: python pet_app.py
2. 打包后: 双击 dist/MilkPet/MilkPet.exe
"""

import sys
import os


def main():
    import io
    
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setApplicationName("Milk Pet")
    app.setQuitOnLastWindowClosed(False)
    
    # 单实例检查
    from games.single_instance import check_single_instance, release_instance
    if not check_single_instance("MilkPet", show_message=True):
        print("[INFO] 检测到重复启动，程序退出")
        return
    
    from desktop_pet import DesktopPet
    
    pet = DesktopPet()
    pet.show()
    
    print("[OK] Milk Pet 已启动！")
    print("[INFO] 右键点击桌宠打开菜单")
    print("[INFO] 关闭窗口会最小化到系统托盘")
    
    exit_code = app.exec_()
    
    # 释放单实例锁
    release_instance()
    
    print("[INFO] Milk Pet 已退出")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()