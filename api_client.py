# api_client.py

import os
from openai import OpenAI
from typing import List, Dict, Any
import re
import json

from config import BASE_URL, XIAOAI_API_KEY, MODEL_ID


class OpenAIClient:
    """使用 OpenAI 库调用 OpenAI API"""

    def __init__(self):
        self.client = OpenAI(
            api_key=XIAOAI_API_KEY,
            base_url=BASE_URL
        )
        self.model_id = MODEL_ID

    def analyze_template(self, prompt: str) -> Dict:
        """分析模板结构"""
        try:
            full_prompt = (
                "你是一个专业的文本分析助手，请按照以下格式分析英文段落：\n"
                "```json\n"
                "{\n"
                "  \"discourse_structure\": {...},\n"
                "  \"content_structure\": {...}\n"
                "}\n"
                "```"
                + "\n" + prompt
            )

            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                n=1
            )
            return self._parse_api_result(response)
        except Exception as e:
            print(f"API调用错误: {e}")
            return {}

    def generate_paragraph(self, prompt: str) -> str:
        """生成仿写段落"""
        try:
            full_prompt = (
                    "你是一个专业的英文段落生成助手，请根据给定的结构和主题生成一个连贯的英文段落。"
                    + "\n" + prompt
            )

            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                n=1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API调用错误: {e}")
            return ""

    def _parse_api_result(self, result) -> Dict:
        """解析 OpenAI API 返回的结果"""
        content = result.choices[0].message.content.strip()

        # 尝试从返回内容中提取 JSON 格式的数据
        try:
            # 提取代码块中的 JSON 内容
            match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
            if match:
                json_content = match.group(1)
                return json.loads(json_content)

            # 如果没有找到代码块，尝试直接解析整个内容
            return json.loads(content)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"无法解析 API 返回的 JSON 数据: {e}")
            return {"raw_response": content}

    def batch_process(self, prompts: List[str], process_type: str) -> List[Any]:
        """批量处理多个提示"""
        results = []
        method = self.analyze_template if process_type == "analysis" else self.generate_paragraph

        for prompt in prompts:
            result = method(prompt)
            results.append(result)

        return results

    def test_connection(self) -> bool:
        """测试 API 连接是否正常"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []








