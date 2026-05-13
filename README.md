# 🐱 Milk Pet - 桌面宠物应用

一款基于 PyQt5 开发的可爱桌面宠物应用，陪伴你的工作与生活。

## ✨ 功能特性

### 🐾 宠物系统
- 可爱的桌面宠物，支持拖拽移动
- 宠物属性系统（饱食度、饥渴值、心情）
- 属性自然衰减机制，需要定期照料
- 经验值与等级系统
- 系统托盘最小化，不占用任务栏空间

### 🎮 游戏娱乐
- **数字华容道**：经典滑块拼图游戏（简单/普通/困难）
- **数独游戏**：逻辑推理游戏（简单/中等/困难）
- 游戏完成可获得经验奖励

### 💰 经济系统
- 喵币自动获取（每5分钟+5枚）
- 离线收益机制（上限100枚）
- 商店系统：购买各种物品
- 背包系统：管理已购买的物品

### 📊 数据统计
- 成就系统
- 游戏统计
- 使用数据记录

## 📁 项目结构

```
MilkPet/
├── desktop_pet.py          # 桌宠主控制器
├── pet_app.py              # 应用入口
├── pet/                    # 宠物模块
│   ├── pet_display.py      # 宠物显示核心
│   ├── pet_stats.py        # 属性管理
│   └── pet_tray.py         # 系统托盘
├── games/                  # 游戏模块
│   ├── dh_puzzle.py        # 数字华容道
│   └── sudoku.py           # 数独游戏
├── basic_model/            # 核心模型
│   ├── inventory.py        # 背包系统
│   ├── items.py            # 物品定义
│   ├── shop.py             # 商店系统
│   ├── statistics.py       # 统计数据
│   └── secure_storage.py   # 安全存储
├── config/                 # 配置文件
│   ├── settings.py         # 游戏参数配置
│   ├── item_settings.py    # 物品配置
│   └── styles.py           # UI样式
├── widgets/                # 自定义组件
│   ├── dialog.py           # 对话框
│   ├── game_success_window.py  # 游戏胜利窗口
│   └── pet_stat_bar.py     # 属性条组件
├── assets/images/          # 图片资源
│   ├── items/              # 物品图标
│   ├── sliding_puzzle/     # 拼图资源
│   └── ...                 # 其他资源
└── dist/MilkPet/           # 打包后的可执行文件
```

## 🚀 快速开始

### 环境要求
- Python 3.x
- PyQt5

### 安装依赖

```bash
pip install PyQt5
```

### 运行项目

```bash
# 方式一：直接运行源码
python pet_app.py

# 方式二：运行打包后的程序
cd dist/MilkPet
MilkPet.exe
```

## 🎯 使用说明

### 基本操作
1. **启动应用**：运行 `pet_app.py` 或双击 `MilkPet.exe`
2. **右键菜单**：右键点击宠物打开功能菜单
3. **移动宠物**：鼠标拖拽宠物到任意位置
4. **最小化**：关闭窗口会最小化到系统托盘

### 功能菜单
- 🍖 **喂食**：恢复饱食度
- 💧 **喝水**：恢复饥渴值
- 🎮 **玩游戏**：选择华容道或数独
- 🛒 **商店**：购买物品
- 🎒 **背包**：查看已购物品
- 📊 **统计**：查看成就和数据

## ⚙️ 配置说明

所有可调整的参数都在 [config/settings.py](config/settings.py) 中：

- **喵币获取**：`COIN_AUTO_INTERVAL`（间隔）、`COIN_AUTO_AMOUNT`（数量）
- **属性衰减**：`PET_DECAY_*`（每秒衰减量）
- **等级系统**：`LEVEL_EXP`（每级所需经验）
- **游戏奖励**：`GAME_EXP_REWARD`（各游戏难度经验值）

## 🔨 打包发布

使用 PyInstaller 打包：

```bash
pyinstaller MilkPet.spec
```

打包后的文件在 `dist/MilkPet/` 目录下。

## 📝 技术特点

- **单实例运行**：防止重复启动
- **数据持久化**：安全存储玩家数据
- **模块化设计**：清晰的代码结构，易于扩展
- **响应式UI**：基于 PyQt5 的现代化界面

## 📄 许可证

本项目仅供学习和个人使用。

## 🙏 致谢

感谢所有为开源社区贡献的开发者！
