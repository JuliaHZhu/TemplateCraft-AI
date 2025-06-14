import os
from openai import OpenAI
from typing import List, Dict, Any
import re
import json

from config import BASE_URL, ARK_API_KEY, MODEL_ID


class OpenAIClient:
    """使用openai库调用OpenAI API"""

    def __init__(self):
        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=ARK_API_KEY
        )
        self.model_id = MODEL_ID

    def analyze_template(self, prompt: str) -> Dict:
        """分析模板结构"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的文本分析助手，请按照以下格式分析英文段落：\n```json\n{\n\"discourse_structure\": {...},\n\"content_structure\": {...}\n}\n```"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return self._parse_api_result(response)
        except Exception as e:
            print(f"API调用错误: {e}")
            return {}

    def generate_paragraph(self, prompt: str) -> str:
        """生成仿写段落"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的英文段落生成助手，请根据给定的结构和主题生成一个连贯的英文段落。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API调用错误: {e}")
            return ""

    def _parse_api_result(self, result) -> Dict:
        """解析OpenAI API返回的结果"""
        content = result.choices[0].message.content

        # 尝试从返回内容中提取JSON格式的数据
        try:
            # 提取代码块中的JSON内容
            match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if match:
                json_content = match.group(1)
                return json.loads(json_content)

            # 如果没有找到代码块，尝试直接解析整个内容
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            print("无法解析API返回的JSON数据")
            return {"raw_response": content}

    def batch_process(self, prompts: List[str], process_type: str) -> List[str]:
        """批量处理多个提示"""
        results = []
        method = self.analyze_template if process_type == "analysis" else self.generate_paragraph

        for prompt in prompts:
            result = method(prompt)
            results.append(result)

        return results