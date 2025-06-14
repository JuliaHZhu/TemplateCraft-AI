import requests
import json
import re
from typing import List, Dict, Any
from config import ARK_API_KEY, BASE_URL, MODEL_ID


class VolcengineAPIClient:
    """使用原生HTTP请求调用火山引擎API，保持与官方SDK一致的参数命名"""

    def __init__(self):
        self.api_key = ARK_API_KEY
        self.base_url = BASE_URL
        self.model_id = MODEL_ID
        self.api_endpoint = f"{self.base_url}/chat/completions"

    def analyze_template(self, prompt: str) -> Dict:
        """分析模板结构"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"  # 与官方示例保持一致的认证方式
        }

        payload = {
            "model": self.model_id,  # 与官方示例保持一致的模型参数名
            "messages": [
                {"role": "system",
                 "content": "你是一个专业的文本分析助手，请按照以下格式分析英文段落：\n```json\n{\n\"discourse_structure\": {...},\n\"content_structure\": {...}\n}\n```"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return self._parse_api_result(result)
        except Exception as e:
            print(f"API调用错误: {e}")
            if hasattr(e, 'response'):
                print(f"响应内容: {e.response.text}")
            return {}

    def generate_paragraph(self, prompt: str) -> str:
        """生成仿写段落"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"  # 与官方示例保持一致
        }

        payload = {
            "model": self.model_id,  # 与官方示例保持一致
            "messages": [
                {"role": "system",
                 "content": "你是一个专业的英文段落生成助手，请根据给定的结构和主题生成一个连贯的英文段落。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            print(f"API调用错误: {e}")
            if hasattr(e, 'response'):
                print(f"响应内容: {e.response.text}")
            return ""

    # 其他方法保持不变...