# 🐱 Milk Pet - 桌面宠物应用

一款基于 PyQt5 开发的可爱桌面宠物应用，陪伴你的工作与生活。

## ✨ 功能特性

### 🐾 宠物系统
- 可爱的桌面宠物，支持拖拽移动
- 宠物属性系统（饱食度、饥渴值、心情）
- 属性自然衰减机制，需要定期照料
- 经验值与等级系统
- 系统托盘最小化，不占用任务栏空间
- 点击触发动画效果（3秒冷却时间）

### 💬 对话系统
- 点击对话：点击宠物随机显示对话内容
- 自动对话：每10分钟自动弹出对话
- 对话窗口3秒后自动关闭
- 可配置对话内容（[config/talk_config.py](config/talk_config.py)）

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
├── pet_app.py              # 应用入口
├── desktop_pet.py          # 桌宠主控制器
├── build_exe.py            # 打包工具脚本
├── MilkPet.spec            # PyInstaller 配置
├── MilkPet.iss             # Inno Setup 安装包配置
│
├── pet/                    # 宠物模块
│   ├── pet_display.py      # 宠物显示核心
│   ├── pet_stats.py        # 属性管理
│   └── pet_tray.py         # 系统托盘
│
├── games/                  # 游戏模块
│   ├── dh_puzzle.py        # 数字华容道
│   └── sudoku.py           # 数独游戏
│
├── basic_model/            # 核心模型
│   ├── inventory.py        # 背包系统
│   ├── items.py            # 物品定义
│   ├── shop.py             # 商店系统
│   ├── statistics.py       # 统计数据
│   └── secure_storage.py   # 安全存储
│
├── config/                 # 配置文件
│   ├── settings.py         # 游戏参数配置
│   ├── item_settings.py    # 物品配置
│   ├── talk_config.py      # 对话配置
│   └── styles.py           # UI样式
│
├── widgets/                # 自定义组件
│   ├── dialog.py           # 对话框
│   ├── talk_window.py      # 对话窗口
│   ├── game_success_window.py  # 游戏胜利窗口
│   └── pet_stat_bar.py     # 属性条组件
│
└── assets/images/          # 图片资源
    ├── logo.ico            # 应用图标
    ├── items/              # 物品图标
    ├── sliding_puzzle/     # 拼图资源
    ├── pet/                # 宠物动画帧
    └── talk.png            # 对话框背景
```

## 🚀 快速开始

### 环境要求
- Python 3.x
- PyQt5
- Inno Setup 6（生成安装包时需要）

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
./MilkPet.exe          # Windows
```

## 📦 打包发布

### 一键打包命令

```bash
# 1️⃣ 仅打包 EXE
python build_exe.py

# 2️⃣ 仅生成安装包（需要先打包 EXE）
python build_exe.py --installer

# 3️⃣ 一键完成：打包 EXE + 生成安装包 ⭐ 推荐
python build_exe.py --all

# 其他选项
python build_exe.py --simple   # 单文件模式
python build_exe.py --test     # 测试模式
python build_exe.py --help     # 查看帮助
```

### 打包后的文件结构

```
dist/MilkPet/                    # EXE 输出目录
├── MilkPet.exe                  # 主程序（~18 MB）
└── _internal/                   # 运行时依赖文件
    ├── python314.dll            # Python 运行时
    ├── assets/images/           # 图片资源
    └── ...                      # 其他依赖文件

installer/                       # 安装包输出目录
└── MilkPet_Setup_1.0.0.exe      # Windows 安装程序（~28 MB）
```

### 安装包功能

使用 [Inno Setup](https://jrsoftware.org/isdl.php) 生成的安装程序支持：

- ✅ **自定义安装路径**：用户可选择安装目录
- ✅ **桌面快捷方式**：可选创建
- ✅ **开始菜单快捷方式**：自动添加到程序组
- ✅ **卸载程序**：包含卸载功能，保留用户数据
- ✅ **注册表记录**：记录安装路径等信息

### 安装后目录结构

```
{安装目录}/Milk Pet/
├── MilkPet.exe        # 主程序
└── _internal/         # 数据目录
```

## 🎯 使用说明

### 基本操作
1. **启动应用**：运行 `pet_app.py` 或双击 `MilkPet.exe`
2. **右键菜单**：右键点击宠物打开功能菜单
3. **移动宠物**：鼠标拖拽宠物到任意位置（可通过设置禁用）
4. **最小化**：关闭窗口会最小化到系统托盘
5. **点击互动**：左键点击宠物触发动画和对话

### 功能菜单
- 🍖 **喂食**：恢复饱食度
- 💧 **喝水**：恢复饥渴值
- 🎮 **玩游戏**：选择华容道或数独
- 🛒 **商店**：购买物品
- 🎒 **背包**：查看已购物品
- 📊 **统计**：查看成就和数据
- ⚙️ **设置**：
  - 允许/禁止移动宠物
  - 最小化到托盘设置

## ⚙️ 配置说明

所有可调整的参数都在 `config/` 目录下：

| 文件 | 说明 | 主要配置项 |
|------|------|-----------|
| [settings.py](config/settings.py) | 游戏参数 | 喵币获取、属性衰减、等级系统、游戏奖励 |
| [item_settings.py](config/item_settings.py) | 物品配置 | 物品价格、效果、描述 |
| [talk_config.py](config/talk_config.py) | 对话配置 | 点击对话列表、自动对话列表、时间间隔 |
| [styles.py](config/styles.py) | UI样式 | 颜色方案、字体大小 |

## 🔧 开发指南

### 技术栈
- **GUI框架**：PyQt5
- **打包工具**：PyInstaller 6.20.0
- **安装包**：Inno Setup 6.7.1
- **Python版本**：3.14.3

### 扩展开发
1. **添加新游戏**：在 `games/` 目录创建新的游戏模块
2. **添加新物品**：修改 `basic_model/items.py` 和 `basic_model/shop.py`
3. **修改对话内容**：编辑 `config/talk_config.py`
4. **调整UI样式**：修改 `config/styles.py`

## 📝 技术特点

- **单实例运行**：防止重复启动
- **数据持久化**：安全存储玩家数据（使用 AES 加密）
- **模块化设计**：清晰的代码结构，易于扩展
- **响应式UI**：基于 PyQt5 的现代化界面
- **动画系统**：支持帧动画和点击交互
- **跨平台兼容**：Windows 10/11 支持

## 📄 许可证

本项目仅供学习和个人使用。

## 🙏 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [PyInstaller](https://www.pyinstaller.org/) - 打包工具
- [Inno Setup](https://jrsoftware.org/isinfo.php) - 安装包制作工具