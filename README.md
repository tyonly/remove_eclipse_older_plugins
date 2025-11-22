# Eclipse 插件清理工具

智能清理Eclipse插件目录中的重复旧版本插件，支持自动识别插件目录、安全备份和预览模式。

## 🚀 新版本特性 (smart_plugin_cleaner.py)

- **🔍 自动识别** - 自动查找系统中的Eclipse插件目录
- **📁 智能选择** - 提供目录选择菜单，支持手动输入
- **🛡️ 安全备份** - 删除前自动备份，支持一键恢复
- **👀 预览模式** - 执行前显示将要删除的插件列表
- **⚡ 纯内存处理** - 无需数据库，即开即用
- **🎯 零配置** - 开箱即用，无需任何配置
- **🔄 智能去重** - Windows大小写不敏感，自动去重路径

## 📦 使用方法

### 方法一：自动选择（推荐）
```bash
python smart_plugin_cleaner.py
```
运行后会自动扫描并显示找到的插件目录，用数字选择即可。

### 方法二：直接指定目录
```python
from smart_plugin_cleaner import SmartPluginCleaner

cleaner = SmartPluginCleaner("你的插件目录路径")
cleaner.run()
```

## 🔧 功能特性

### 自动识别路径
工具会自动搜索以下位置：
- **Windows注册表** - 优先从注册表查找Eclipse安装信息
- **开始菜单** - 搜索Eclipse快捷方式获取安装路径
- **全盘扫描** - Windows下遍历所有盘符（A-Z）查找Eclipse
- 当前目录及其父目录
- 常见安装位置：`Program Files/Eclipse`, `Dev/eclipse`, `Tools/eclipse` 等
- 用户目录：`~/eclipse`, `~/Eclipse`
- 插件目录：`plugins/`, `dropins/`

### 安全机制
1. **预览确认** - 显示详细的删除计划
2. **自动备份** - 删除前备份到带时间戳的目录
3. **备份清单** - JSON格式的详细备份记录
4. **错误处理** - 完善的异常捕获和回滚机制

### 版本比较
- 支持标准版本号：`1.2.3`, `2.0.1`
- 支持Eclipse格式：`1.2.3.v20200101-1000`
- 智能解析：自动提取主版本号进行比较

## 📁 旧版本说明 (removeChongfuPlugin.py)

> ⚠️ **已废弃** - 需要MySQL数据库，配置复杂，建议使用新版本

如果需要使用旧版本：
1. 导入 `plugins.sql` 到数据库
2. 修改数据库连接参数
3. 复制到插件目录运行

## 🛠️ 开发环境

- **Python 3.6+**
- **无外部依赖** - 仅使用Python标准库
- **跨平台** - 支持 Windows、macOS、Linux

## 🔒 安全说明

- 工具只会删除重复的旧版本插件
- 每次操作前都会创建备份
- 支持预览模式，可查看将要删除的文件
- 保留最新版本，确保系统稳定性

## 📄 许可证

本项目采用 MIT 许可证，可自由使用和修改。

---

# Eclipse Plugin Cleaner

Smart cleaner for duplicate old version plugins in Eclipse plugin directories, with auto-detection, safe backup, and preview mode.

## 🚀 New Features (smart_plugin_cleaner.py)

- **🔍 Auto Detection** - Automatically finds Eclipse plugin directories
- **📁 Smart Selection** - Provides directory selection menu with manual input support
- **🛡️ Safe Backup** - Auto-backup before deletion with one-click restore
- **👀 Preview Mode** - Shows plugins to be deleted before execution
- **⚡ In-Memory Processing** - No database required, ready to use
- **🎯 Zero Configuration** - Out of the box, no configuration needed
- **🔄 Smart Deduplication** - Windows case-insensitive, auto-duplicate removal

## 📦 Usage

### Method 1: Auto Selection (Recommended)
```bash
python smart_plugin_cleaner.py
```
Automatically scans and displays found plugin directories, select with number.

### Method 2: Direct Directory Specification
```python
from smart_plugin_cleaner import SmartPluginCleaner

cleaner = SmartPluginCleaner("Your plugin directory path")
cleaner.run()
```

## 🔧 Features

### Auto Path Detection
Tool automatically searches the following locations:
- **Windows Registry** - Priority search for Eclipse installation info in registry
- **Start Menu** - Search Eclipse shortcuts to get installation path
- **Full Drive Scanning** - Windows scans all drives (A-Z) for Eclipse
- Current directory and its parent directories
- Common installation locations: `Program Files/Eclipse`, `Dev/eclipse`, `Tools/eclipse`, etc.
- User directories: `~/eclipse`, `~/Eclipse`
- Plugin directories: `plugins/`, `dropins/`

### Safety Mechanisms
1. **Preview Confirmation** - Shows detailed deletion plan
2. **Auto Backup** - Backup to timestamped directory before deletion
3. **Backup Manifest** - Detailed backup record in JSON format
4. **Error Handling** - Comprehensive exception handling and rollback

### Version Comparison
- Supports standard version numbers: `1.2.3`, `2.0.1`
- Supports Eclipse format: `1.2.3.v20200101-1000`
- Smart parsing: auto-extract main version for comparison

## 📁 Legacy Version (removeChongfuPlugin.py)

> ⚠️ **Deprecated** - Requires MySQL database, complex configuration, recommend using new version

If you need to use the legacy version:
1. Import `plugins.sql` to database
2. Modify database connection parameters
3. Copy to plugin directory and run

## 🛠️ Development Environment

- **Python 3.6+**
- **No External Dependencies** - Only uses Python standard library
- **Cross Platform** - Supports Windows, macOS, Linux

## 🔒 Security Notes

- Tool only deletes duplicate old version plugins
- Creates backup before each operation
- Supports preview mode to view files to be deleted
- Keeps latest version to ensure system stability

## 📄 License

This project is licensed under MIT License, free to use and modify.