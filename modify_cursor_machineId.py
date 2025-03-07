#!/usr/bin/env python
# coding=utf-8
import os
import json
import uuid
import psutil
import time

def is_cursor_running():
    """检查 Cursor 是否正在运行"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 检查进程名称是否包含 "Cursor"
            if 'Cursor' in proc.info['name'] and 'CursorUIViewService' not in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def close_cursor():
    """关闭 Cursor 进程"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'Cursor' in proc.info['name'] and 'CursorUIViewService' not in proc.info['name']:
                print(f"Closing Cursor (PID: {proc.info['pid']}, Name: {proc.info['name']})...")
                proc.terminate()  # 终止进程
                try:
                    proc.wait(timeout=3)  # 等待进程结束，最多 3 秒
                except psutil.TimeoutExpired:
                    print(f"Timeout while waiting for Cursor (PID: {proc.info['pid']}) to close.")
                except psutil.NoSuchProcess:
                    print(f"Cursor (PID: {proc.info['pid']}) already closed.")
                time.sleep(1)  # 等待 1 秒确保进程已关闭
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def modify_cursor_machine_id():
    # 定义 Cursor 配置文件的路径
    if os.name == 'nt':  # Windows 系统
        config_path = os.path.expandvars(r'%APPDATA%\Cursor\User\globalStorage\storage.json')
    elif os.name == 'posix':  # macOS 或 Linux 系统
        config_path = os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/storage.json')
    else:
        print("Unsupported operating system.")
        return

    # 检查 Cursor 是否正在运行
    if is_cursor_running():
        print("Cursor is running. Attempting to close it...")
        close_cursor()
        time.sleep(3)
        if is_cursor_running():
            print("Failed to close Cursor. Please close it manually and try again.")
            return
        else:
            print("Cursor closed successfully.")

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        print(f"Cursor configuration file not found at: {config_path}")
        return

    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
    except Exception as e:
        print(f"Failed to read configuration file: {e}")
        return

    # 生成新的机器码
    new_machine_id = str(uuid.uuid4())
    new_mac_machine_id = str(uuid.uuid4())
    new_dev_device_id = str(uuid.uuid4())
    new_sqm_id = str(uuid.uuid4()) if os.name == 'nt' else None

    # 修改机器码字段
    config_data['telemetry.machineId'] = new_machine_id
    config_data['telemetry.macMachineId'] = new_mac_machine_id
    config_data['telemetry.devDeviceId'] = new_dev_device_id
    if os.name == 'nt':
        config_data['telemetry.sqmId'] = new_sqm_id

    # 保存修改后的配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config_data, file, indent=4)
        print("Cursor machine IDs modified successfully!")
        print(f"New telemetry.machineId: {new_machine_id}")
        print(f"New telemetry.macMachineId: {new_mac_machine_id}")
        print(f"New telemetry.devDeviceId: {new_dev_device_id}")
        if os.name == 'nt':
            print(f"New telemetry.sqmId: {new_sqm_id}")
    except Exception as e:
        print(f"Failed to save configuration file: {e}")

if __name__ == "__main__":
    modify_cursor_machine_id()
