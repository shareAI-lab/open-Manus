#!/usr/bin/env python
from pathlib import Path
import subprocess
import sys
from typing import List, Optional
from functools import partial

def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """执行命令行指令"""
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def generate_requirements(project_root: Path) -> None:
    """生成 requirements.txt 和 lock 文件"""
    commands = [
        ["uv", "pip", "freeze"],
        ["uv", "pip", "compile", "requirements.txt", "-o", "requirements.lock"]
    ]
    
    try:
        # 生成 requirements.txt
        result = run_command(commands[0])
        requirements_path = project_root / "requirements.txt"
        requirements_path.write_text(result.stdout)
        print("✅ 已生成 requirements.txt")
        
        # 生成 lock 文件
        run_command(commands[1])
        print("✅ 已生成 requirements.lock")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败: {e.stderr}")
        sys.exit(1)

def install_deps(use_lock: bool = False) -> None:
    """安装依赖"""
    cmd = ["uv", "pip"]
    cmd.extend(["sync", "requirements.lock"] if use_lock else ["install", "-r", "requirements.txt"])
    
    try:
        run_command(cmd)
        print(f"✅ 已{'从 lock 文件' if use_lock else ''}安装依赖")
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e.stderr}")
        sys.exit(1)

def main() -> None:
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    if len(sys.argv) < 2:
        print("请指定操作: generate, install, sync")
        sys.exit(1)
        
    commands = {
        "generate": lambda: generate_requirements(project_root),
        "install": lambda: install_deps(False),
        "sync": lambda: install_deps(True)
    }
    
    action = sys.argv[1]
    if action not in commands:
        print(f"未知操作: {action}")
        print("可用操作: generate, install, sync")
        sys.exit(1)
        
    commands[action]()

if __name__ == "__main__":
    main()