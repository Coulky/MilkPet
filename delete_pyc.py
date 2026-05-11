import shutil
import os

folder_path_list = [
    "__pycache__",
    "basic_model/__pycache__",
    "common/__pycache__",
    "config/__pycache__",
    "games/__pycache__",
    "pet/__pycache__",
    "widgets/__pycache__"
    ]


def delete_directory(path):
    """
    安全删除指定目录及其所有子目录和文件。
    参数:
        path: 要删除的目录路径 (字符串)
    """
    try:
        # 1. 检查路径是否存在
        if os.path.exists(path):
            # 2. 检查路径是否确实是一个目录
            if os.path.isdir(path):
                # 3. 递归删除目录及其所有内容
                shutil.rmtree(path)
                print(f"✅ 成功: 目录 '{path}' 及其内容已被删除。")
            else:
                print(f"❌ 错误: 路径 '{path}' 存在，但它不是一个目录。")
        else:
            print(f"⚠️ 提示: 目录 '{path}' 不存在，无需删除。")
            
    except Exception as e:
        pass

# --- 使用示例 ---
if __name__ == "__main__":
    for path in folder_path_list:
        delete_directory(path)