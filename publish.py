#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

def clean_old_builds():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for d in dirs_to_clean:
        try:
            if '*' in d:  # 处理通配符
                import glob
                for path in glob.glob(d):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            elif os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
        except Exception as e:
            print(f"清理 {d} 时出错: {e}")

def run_cmd(cmd, env=None):
    print(f"\n执行命令: {cmd}")
    process = subprocess.run(cmd, shell=True, env=env)
    if process.returncode != 0:
        print(f"命令执行失败: {cmd}")
        sys.exit(1)

def main():
    # 检查是否设置了 PYPI_TOKEN 环境变量
    token = os.environ.get('PYPI_TOKEN')
    if not token:
        print("错误: 未设置 PYPI_TOKEN 环境变量")
        print("请先设置环境变量：")
        print("Windows PowerShell: $env:PYPI_TOKEN='your-token'")
        print("Windows CMD: set PYPI_TOKEN=your-token")
        sys.exit(1)

    # 清理旧的构建
    clean_old_builds()
    
    # 安装必要的工具
    print("\n安装打包工具...")
    run_cmd("pip install -i https://pypi.tuna.tsinghua.edu.cn/simple build twine")
    
    # 构建包
    print("\n构建包...")
    run_cmd("python -m build")
    
    # 上传到PyPI
    print("\n上传到PyPI...")
    env = os.environ.copy()
    env['TWINE_USERNAME'] = '__token__'
    env['TWINE_PASSWORD'] = token
    run_cmd("python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*", env=env)
    
    print("\n发布完成!")
    print("\n用户现在可以通过以下命令安装:")
    print("\npip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyunstuck")

if __name__ == "__main__":
    main() 