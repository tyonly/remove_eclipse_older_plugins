#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import shutil
import json
from datetime import datetime
from collections import defaultdict
import platform

class SmartPluginCleaner:
    def __init__(self, plugin_dir, backup_dir=None):
        self.plugin_dir = plugin_dir
        self.backup_dir = backup_dir or os.path.join(plugin_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.plugins_by_name = defaultdict(list)
        self.to_delete = []
        self.to_keep = []
    
    @staticmethod
    def find_eclipse_from_registry():
        """从Windows注册表查找Eclipse安装路径"""
        if platform.system() != "Windows":
            return []
        
        eclipse_paths = []
        
        try:
            import winreg
            
            # Eclipse可能注册的路径
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Eclipse"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Eclipse"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Wow6432Node\Eclipse"),
                # 一些常见的Eclipse发行版
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\IBM\SDP"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\MyEclipse"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Oracle\Java Development Kit"),
            ]
            
            for hkey, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        # 尝试读取常见的安装路径键值
                        value_names = ["InstallPath", "Path", "Location", "Home", "EclipseHome"]
                        
                        for value_name in value_names:
                            try:
                                value, _ = winreg.QueryValueEx(key, value_name)
                                if value and os.path.exists(value):
                                    eclipse_paths.append(value)
                            except:
                                continue
                        
                        # 如果没有找到特定键值，尝试枚举所有值
                        try:
                            i = 0
                            while True:
                                name, value, _ = winreg.EnumValue(key, i)
                                if isinstance(value, str) and "eclipse" in value.lower():
                                    if os.path.exists(value):
                                        eclipse_paths.append(value)
                                i += 1
                        except:
                            continue
                            
                except:
                    continue
                    
        except ImportError:
            # 如果没有winreg模块，跳过注册表查找
            pass
        except Exception as e:
            print(f"注册表查找出错: {e}")
        
        return SmartPluginCleaner._normalize_and_deduplicate_paths(eclipse_paths)
    
    @staticmethod
    def find_eclipse_from_start_menu():
        """从Windows开始菜单快捷方式查找Eclipse"""
        if platform.system() != "Windows":
            return []
        
        eclipse_paths = []
        
        try:
            # 常见的开始菜单路径
            start_menu_paths = [
                os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
                os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            ]
            
            for start_menu in start_menu_paths:
                if not os.path.exists(start_menu):
                    continue
                
                # 递归查找Eclipse快捷方式
                for root, dirs, files in os.walk(start_menu):
                    for file in files:
                        if file.lower().endswith('.lnk') and 'eclipse' in file.lower():
                            try:
                                import win32com.client
                                shell = win32com.client.Dispatch("WScript.Shell")
                                shortcut = shell.CreateShortCut(os.path.join(root, file))
                                target_path = shortcut.TargetPath
                                
                                if target_path and os.path.exists(target_path):
                                    # 从eclipse.exe路径推导出安装目录
                                    if 'eclipse.exe' in target_path.lower():
                                        eclipse_dir = os.path.dirname(target_path)
                                        eclipse_paths.append(eclipse_dir)
                            except:
                                continue
                                
        except Exception as e:
            print(f"开始菜单查找出错: {e}")
        
        return SmartPluginCleaner._normalize_and_deduplicate_paths(eclipse_paths)
    
    @staticmethod
    def find_eclipse_plugin_dirs():
        """自动查找Eclipse插件目录"""
        plugin_dirs = []
        
        # 1. Windows平台优先从注册表查找
        if platform.system() == "Windows":
            registry_paths = SmartPluginCleaner.find_eclipse_from_registry()
            for path in registry_paths:
                plugin_dirs.extend(SmartPluginCleaner._check_eclipse_installation(path))
            
            # 从开始菜单查找
            start_menu_paths = SmartPluginCleaner.find_eclipse_from_start_menu()
            for path in start_menu_paths:
                plugin_dirs.extend(SmartPluginCleaner._check_eclipse_installation(path))
        
        # 2. 常见的Eclipse安装路径
        search_paths = []
        
        # Windows系统：遍历所有可用盘符
        if platform.system() == "Windows":
            import string
            for drive in string.ascii_uppercase:
                drive_path = f"{drive}:/"
                if os.path.exists(drive_path):
                    # 每个盘符的常见安装位置
                    search_paths.extend([
                        f"{drive}:/eclipse",
                        f"{drive}:/Eclipse",
                        f"{drive}:/Program Files/Eclipse",
                        f"{drive}:/Program Files (x86)/Eclipse",
                        f"{drive}:/ProgramData/Eclipse",
                        f"{drive}:/Users/%USERNAME%/eclipse",
                        f"{drive}:/Dev/eclipse",
                        f"{drive}:/Tools/eclipse",
                        f"{drive}:/IDE/eclipse"
                    ])
        else:
            # 非Windows系统的常见路径
            search_paths.extend([
                os.path.expanduser("~/eclipse"),
                os.path.expanduser("~/Eclipse"),
                "/opt/eclipse",
                "/usr/local/eclipse",
                "/usr/share/eclipse",
                "/Applications/Eclipse.app/Contents/Eclipse",
                "/home/eclipse",
                "/usr/eclipse"
            ])
        
        # 3. 搜索当前目录及其父目录
        current_dir = os.getcwd()
        for i in range(5):  # 向上搜索5层目录
            search_paths.append(current_dir)
            parent = os.path.dirname(current_dir)
            if parent == current_dir:  # 已到达根目录
                break
            current_dir = parent
        
        # 搜索所有可能的路径
        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            
            plugin_dirs.extend(SmartPluginCleaner._check_eclipse_installation(base_path))
        
        # 去重并排序（Windows大小写不敏感处理）
        plugin_dirs = SmartPluginCleaner._normalize_and_deduplicate_paths(plugin_dirs)
        
        return plugin_dirs
    
    @staticmethod
    def _normalize_and_deduplicate_paths(paths):
        """标准化路径并去重，处理Windows大小写不敏感问题"""
        if not paths:
            return []
        
        # Windows平台大小写不敏感，但保持原始显示格式
        if platform.system() == "Windows":
            # 使用字典记录已见过的路径（小写键，原始值）
            seen_paths = {}
            normalized_paths = []
            
            for path in paths:
                # 标准化路径（处理斜杠、点号等）
                normalized_path = os.path.normpath(path)
                # Windows下转换为小写进行比较，但保存原始格式
                path_key = normalized_path.lower()
                
                if path_key not in seen_paths:
                    seen_paths[path_key] = normalized_path
                    normalized_paths.append(normalized_path)
            
            return sorted(normalized_paths)
        else:
            # 非Windows系统，正常去重
            unique_paths = list(set(os.path.normpath(p) for p in paths))
            return sorted(unique_paths)
    
    @staticmethod
    def get_available_drives():
        """获取Windows系统所有可用盘符"""
        if platform.system() != "Windows":
            return []
        
        drives = []
        import string
        
        for drive in string.ascii_uppercase:
            drive_path = f"{drive}:/"
            if os.path.exists(drive_path):
                drives.append(drive_path)
        
        return drives
    
    @staticmethod
    def _check_eclipse_installation(base_path):
        """检查给定的Eclipse安装路径，返回插件目录列表"""
        plugin_dirs = []
        
        # 查找plugins目录
        plugins_path = os.path.join(base_path, "plugins")
        if os.path.exists(plugins_path) and os.path.isdir(plugins_path):
            # 检查是否真的包含插件文件
            has_plugins = False
            try:
                for item in os.listdir(plugins_path)[:10]:  # 只检查前10个文件
                    if item.endswith('.jar') or os.path.isdir(os.path.join(plugins_path, item)):
                        has_plugins = True
                        break
            except:
                pass
            
            if has_plugins:
                plugin_dirs.append(plugins_path)
        
        # 也搜索dropins目录
        dropins_path = os.path.join(base_path, "dropins")
        if os.path.exists(dropins_path) and os.path.isdir(dropins_path):
            plugin_dirs.append(dropins_path)
        
        return plugin_dirs
    
    @staticmethod
    def _normalize_and_deduplicate_paths(paths):
        """标准化路径并去重，处理Windows大小写不敏感问题"""
        if not paths:
            return []
        
        # Windows平台大小写不敏感，但保持原始显示格式
        if platform.system() == "Windows":
            # 使用字典记录已见过的路径（小写键，原始值）
            seen_paths = {}
            normalized_paths = []
            
            for path in paths:
                # 标准化路径（处理斜杠、点号等）
                normalized_path = os.path.normpath(path)
                # Windows下转换为小写进行比较，但保存原始格式
                path_key = normalized_path.lower()
                
                if path_key not in seen_paths:
                    seen_paths[path_key] = normalized_path
                    normalized_paths.append(normalized_path)
            
            return sorted(normalized_paths)
        else:
            # 非Windows系统，正常去重
            unique_paths = list(set(os.path.normpath(p) for p in paths))
            return sorted(unique_paths)
    
    @staticmethod
    def get_available_drives():
        """获取Windows系统所有可用盘符"""
        if platform.system() != "Windows":
            return []
        
        drives = []
        import string
        
        for drive in string.ascii_uppercase:
            drive_path = f"{drive}:/"
            if os.path.exists(drive_path):
                drives.append(drive_path)
        
        return drives
    
    @staticmethod
    def select_plugin_dir():
        """让用户选择插件目录"""
        print("=== Eclipse 插件目录选择 ===\n")
        
        # 自动查找插件目录
        found_dirs = SmartPluginCleaner.find_eclipse_plugin_dirs()
        
        # 添加当前目录选项
        current_dir = os.getcwd()
        if current_dir not in found_dirs:
            found_dirs.insert(0, current_dir)
        
        print("找到以下可能的插件目录:")
        for i, dir_path in enumerate(found_dirs, 1):
            # 显示目录中的一些插件文件作为参考
            try:
                sample_files = []
                for item in os.listdir(dir_path)[:5]:
                    if item.endswith('.jar') or os.path.isdir(os.path.join(dir_path, item)):
                        sample_files.append(item)
                        if len(sample_files) >= 3:
                            break
                
                sample_info = f" (包含: {', '.join(sample_files)})" if sample_files else ""
                print(f"  {i}. {dir_path}{sample_info}")
            except:
                print(f"  {i}. {dir_path}")
        
        print(f"  {len(found_dirs) + 1}. 手动输入路径")
        print(f"  0. 使用当前目录 ({current_dir})")
        
        while True:
            try:
                choice = input(f"\n请选择插件目录 (0-{len(found_dirs) + 1}): ").strip()
                
                if choice == "0":
                    return current_dir
                elif choice == str(len(found_dirs) + 1):
                    # 手动输入
                    custom_path = input("请输入插件目录路径: ").strip().strip('"\'')
                    if os.path.exists(custom_path) and os.path.isdir(custom_path):
                        return custom_path
                    else:
                        print("错误: 路径不存在或不是目录")
                        continue
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(found_dirs):
                        return found_dirs[choice_num - 1]
                    else:
                        print(f"请输入 0-{len(found_dirs) + 1} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n用户取消操作")
                return None
        
    def parse_plugin_info(self, filename):
        """解析插件信息，返回(name, version, full_version)"""
        original_name = filename
        is_dir = os.path.isdir(os.path.join(self.plugin_dir, filename))
        
        if filename.endswith('.jar'):
            filename = filename[:-4]
        
        # 处理格式: pluginname_1.2.3.v20200101-1000
        if '_' not in filename:
            return original_name, None, None, is_dir
        
        parts = filename.rsplit('_', 1)
        name = parts[0]
        version_str = parts[1]
        
        # 提取主版本号 (1.2.3.v20200101-1000 -> 1.2.3)
        main_version = re.split(r'\.v', version_str)[0] if '.v' in version_str else version_str
        
        return original_name, name, main_version, is_dir
    
    def version_to_tuple(self, version_str):
        """将版本字符串转换为可比较的元组"""
        if not version_str:
            return (0, 0, 0)
        
        # 移除非数字字符，只保留数字和点
        clean_version = re.sub(r'[^\d.]', '', version_str)
        
        # 分割版本号并转换为整数
        parts = [int(x) for x in clean_version.split('.')]
        
        # 补齐到4位 (major.minor.patch.build)
        while len(parts) < 4:
            parts.append(0)
        
        return tuple(parts[:4])
    
    def scan_plugins(self):
        """扫描插件目录"""
        print(f"扫描插件目录: {self.plugin_dir}")
        
        if not os.path.exists(self.plugin_dir):
            print(f"错误: 目录 {self.plugin_dir} 不存在")
            return False
        
        for item in os.listdir(self.plugin_dir):
            # 跳过备份目录
            if item.startswith('backup_'):
                continue
                
            item_path = os.path.join(self.plugin_dir, item)
            
            # 跳过当前脚本文件
            if item == os.path.basename(__file__):
                continue
            
            original_name, name, version, is_dir = self.parse_plugin_info(item)
            
            if name and version:
                self.plugins_by_name[name].append({
                    'original_name': original_name,
                    'name': name,
                    'version': version,
                    'version_tuple': self.version_to_tuple(version),
                    'is_dir': is_dir,
                    'path': item_path
                })
        
        print(f"发现 {len(self.plugins_by_name)} 种插件")
        return True
    
    def analyze_duplicates(self):
        """分析重复插件"""
        for name, plugins in self.plugins_by_name.items():
            if len(plugins) > 1:
                # 按版本排序（从高到低）
                sorted_plugins = sorted(plugins, key=lambda x: x['version_tuple'], reverse=True)
                
                # 保留最新的，其余标记为待删除
                latest = sorted_plugins[0]
                to_delete_list = sorted_plugins[1:]
                
                self.to_keep.append(latest)
                self.to_delete.extend(to_delete_list)
            else:
                # 只有一个版本的插件保留
                self.to_keep.extend(plugins)
        
        print(f"\n分析结果:")
        print(f"  保留插件: {len(self.to_keep)} 个")
        print(f"  删除插件: {len(self.to_delete)} 个")
    
    def preview_changes(self):
        """预览将要删除的插件"""
        if not self.to_delete:
            print("没有发现重复插件")
            return True
        
        print("\n=== 将要删除的插件 ===")
        
        # 按插件名分组显示
        delete_by_name = defaultdict(list)
        for plugin in self.to_delete:
            delete_by_name[plugin['name']].append(plugin)
        
        for name, plugins in delete_by_name.items():
            print(f"\n插件: {name}")
            
            # 找到对应的保留插件
            keep_plugin = next((p for p in self.to_keep if p['name'] == name), None)
            if keep_plugin:
                print(f"  保留: {keep_plugin['original_name']} (v{keep_plugin['version']})")
            
            for plugin in plugins:
                print(f"  删除: {plugin['original_name']} (v{plugin['version']})")
        
        return input(f"\n确认删除这 {len(self.to_delete)} 个插件吗? (y/N): ").lower() == 'y'
    
    def create_backup(self):
        """创建备份"""
        if not self.to_delete:
            return True
        
        print(f"\n创建备份到: {self.backup_dir}")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 创建备份清单
            backup_manifest = {
                'timestamp': datetime.now().isoformat(),
                'source_dir': self.plugin_dir,
                'deleted_plugins': []
            }
            
            for plugin in self.to_delete:
                backup_path = os.path.join(self.backup_dir, plugin['original_name'])
                backup_manifest['deleted_plugins'].append({
                    'original_name': plugin['original_name'],
                    'name': plugin['name'],
                    'version': plugin['version'],
                    'is_dir': plugin['is_dir']
                })
                
                try:
                    if plugin['is_dir']:
                        shutil.copytree(plugin['path'], backup_path)
                    else:
                        shutil.copy2(plugin['path'], backup_path)
                    print(f"  备份: {plugin['original_name']}")
                except Exception as e:
                    print(f"  备份失败: {plugin['original_name']} - {e}")
                    return False
            
            # 保存备份清单
            manifest_path = os.path.join(self.backup_dir, 'backup_manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(backup_manifest, f, indent=2, ensure_ascii=False)
            
            print("备份完成")
            return True
            
        except Exception as e:
            print(f"备份失败: {e}")
            return False
    
    def delete_plugins(self):
        """删除标记的插件"""
        if not self.to_delete:
            print("没有插件需要删除")
            return True
        
        print(f"\n开始删除 {len(self.to_delete)} 个插件...")
        
        success_count = 0
        for plugin in self.to_delete:
            try:
                if plugin['is_dir']:
                    shutil.rmtree(plugin['path'])
                else:
                    os.remove(plugin['path'])
                print(f"  删除: {plugin['original_name']}")
                success_count += 1
            except Exception as e:
                print(f"  删除失败: {plugin['original_name']} - {e}")
        
        print(f"\n删除完成: 成功 {success_count}/{len(self.to_delete)} 个")
        return success_count == len(self.to_delete)
    
    def run(self, preview_only=False):
        """执行清理流程"""
        print("=== Eclipse 插件清理工具 ===\n")
        
        # 1. 扫描插件
        if not self.scan_plugins():
            return False
        
        # 2. 分析重复插件
        self.analyze_duplicates()
        
        # 3. 预览更改
        if not self.preview_changes():
            print("用户取消操作")
            return False
        
        if preview_only:
            print("仅预览模式，不执行实际删除")
            return True
        
        # 4. 创建备份
        if not self.create_backup():
            print("备份失败，中止操作")
            return False
        
        # 5. 删除插件
        return self.delete_plugins()

def main():
    """主函数"""
    print("=== Eclipse 插件清理工具 ===\n")
    
    # 让用户选择插件目录
    plugin_dir = SmartPluginCleaner.select_plugin_dir()
    
    if plugin_dir is None:
        print("操作已取消")
        return
    
    print(f"\n选择的插件目录: {plugin_dir}")
    
    # 创建清理器实例
    cleaner = SmartPluginCleaner(plugin_dir)
    
    # 运行清理
    success = cleaner.run()
    
    if success:
        print("\n✅ 插件清理完成!")
        if cleaner.backup_dir:
            print(f"📁 备份位置: {cleaner.backup_dir}")
    else:
        print("\n❌ 插件清理失败!")

if __name__ == "__main__":
    main()