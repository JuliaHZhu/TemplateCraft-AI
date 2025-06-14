import os
from dotenv import load_dotenv  # 添加此行

# 加载环境变量
load_dotenv()

# OpenAI API 配置
#OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_api_key_here")
ARK_API_KEY = os.environ.get("ARK_API_KEY")

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # OpenAI API 基础 URL
MODEL_ID = "doubao-1-5-pro-32k-250115"  # 默认使用的模型，可根据需要修改

# 项目路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(PROJECT_ROOT, "source")