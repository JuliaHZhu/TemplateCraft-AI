import os

# 火山引擎API配置 - 严格遵循官方示例命名
ARK_API_KEY = os.environ.get("ARK_API_KEY", "your_api_key_here")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 官方示例中的默认路径
MODEL_ID = "doubao-1-5-pro-32k-250115"  # 模型ID，根据需要修改

# 项目路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(PROJECT_ROOT, "source")