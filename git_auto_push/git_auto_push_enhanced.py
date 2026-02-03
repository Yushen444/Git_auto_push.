import os
import subprocess
import datetime
import socket
from pathlib import Path
import sys

def get_current_ip():
    """获取当前IP地址"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "Unknown IP"

def find_git_root():
    """查找git根目录"""
    current_path = Path.cwd()
    # 向上遍历目录，直到找到.git文件夹
    for parent in [current_path] + list(current_path.parents):
        if (parent / '.git').exists():
            return parent
    return None

def main():
    print("开始执行Git自动推送脚本...")
    
    # 查找git根目录
    git_root = find_git_root()
    if not git_root:
        print("错误: 未找到git仓库")
        return
    
    print(f"Git根目录: {git_root}")
    
    # 切换到git根目录
    os.chdir(git_root)
    
    # 拉取远程更改
    print("正在拉取远程更改...")
    try:
        pull_result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        if pull_result.returncode != 0:
            print(f"拉取失败: {pull_result.stderr}")
        else:
            print(f"拉取成功: {pull_result.stdout}")
    except Exception as e:
        print(f"拉取过程中发生错误: {e}")
    
    # 检查是否有文件需要提交
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        git_status = result.stdout.strip()
        print(f"Git状态: {git_status}")
    except Exception as e:
        print(f"获取Git状态失败: {e}")
        return
    
    if not git_status:
        print("没有需要提交的更改")
        # 即使没有更改也记录日志
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = get_current_ip()
        
        log_entry = f"时间: {current_time}\nIP: {ip_address}\n操作: 自动推送（无更改）\n---\n"
        
        log_file = Path("Push-history.md")
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + log_entry)
        else:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_entry)
        
        print("推送历史已记录")
        return
    
    print(f"检测到有文件需要提交")
    
    try:
        # 获取当前日期作为提交信息
        commit_message = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # git add所有更改的文件
        print("正在添加文件到暂存区...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 检查是否有更改需要提交
        diff_result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                   capture_output=True, text=True)
        if diff_result.returncode != 0:  # 有差异，需要提交
            # git commit
            print(f"正在提交更改，提交信息: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # git push
            print("正在推送到远程仓库...")
            subprocess.run(['git', 'push'], check=True)
            
            print("Git操作成功完成！")
            
            # 记录推送历史
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip_address = get_current_ip()
            
            # 获取推送的详细信息
            log_result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                                      capture_output=True, text=True)
            last_commit = log_result.stdout.strip() if log_result.stdout.strip() else "Unknown"
            
            log_entry = f"时间: {current_time}\nIP: {ip_address}\n操作: 自动推送\n提交: {last_commit}\n---\n"
            
            log_file = Path("Push-history.md")
            
            if log_file.exists():
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("\n" + log_entry)
            else:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(log_entry)
            
            print("推送历史已记录")
        else:
            print("没有更改需要提交")
            
            # 记录推送历史，即使没有更改
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip_address = get_current_ip()
            
            log_entry = f"时间: {current_time}\nIP: {ip_address}\n操作: 自动推送（无更改）\n---\n"
            
            log_file = Path("Push-history.md")
            
            if log_file.exists():
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("\n" + log_entry)
            else:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(log_entry)
            
            print("推送历史已记录")
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")

if __name__ == "__main__":
    main()