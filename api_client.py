import requests
from typing import List, Dict, Any
from config import API_KEY, API_SECRET, API_ENDPOINT


class VolcengineAPIClient:
    """火山引擎API客户端：执行分析和生成任务"""

    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.api_endpoint = API_ENDPOINT

    def analyze_template(self, prompt: str) -> Dict:
        """分析模板结构"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}:{self.api_secret}"
        }

        payload = {
            "model": "chatglm_pro",
            "parameters": {
                "prompt": prompt,
                "temperature": 0.3,
                "max_tokens": 1000
            }
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return json.loads(result.get("result", "{}"))
        except Exception as e:
            print(f"API调用错误: {e}")
            return {}

    def generate_paragraph(self, prompt: str) -> str:
        """生成仿写段落"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}:{self.api_secret}"
        }

        payload = {
            "model": "chatglm_pro",
            "parameters": {
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 300
            }
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result", "")
        except Exception as e:
            print(f"API调用错误: {e}")
            return ""

    def batch_process(self, prompts: List[str], process_type: str) -> List[Any]:
        """批量处理请求"""
        results = []
        process_func = self.analyze_template if process_type == "analysis" else self.generate_paragraph

        for prompt in prompts:
            result = process_func(prompt)
            results.append(result)

        return results