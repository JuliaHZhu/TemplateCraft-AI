import os
import json
import re
from typing import List, Dict, Any

def read_text_file(file_path: str) -> str:
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def write_json_file(data: Any, file_path: str) -> None:
    """写入JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def read_json_file(file_path: str) -> Any:
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {}

def get_case_dirs(source_dir: str) -> List[str]:
    """获取所有案例文件夹路径"""
    case_dirs = []
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path) and item.startswith("case"):
            case_dirs.append(item_path)
    return sorted(case_dirs)