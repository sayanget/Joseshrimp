"""
清理Python缓存文件的脚本
"""
import os
import shutil

def clean_pycache():
    """删除所有__pycache__目录和.pyc文件"""
    count = 0
    for root, dirs, files in os.walk('.'):
        # 删除__pycache__目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"删除: {pycache_path}")
                count += 1
            except Exception as e:
                print(f"无法删除 {pycache_path}: {e}")
        
        # 删除.pyc文件
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"删除: {pyc_path}")
                    count += 1
                except Exception as e:
                    print(f"无法删除 {pyc_path}: {e}")
    
    print(f"\n总共删除了 {count} 个缓存文件/目录")

if __name__ == "__main__":
    clean_pycache()
