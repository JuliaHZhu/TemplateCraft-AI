import os

# 获取环境变量
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

BASE_URL = "https://api.openai.com/v1"
MODEL_ID = "gpt-4"

# 项目路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(PROJECT_ROOT, "source")

