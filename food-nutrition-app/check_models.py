import os
import google.generativeai as genai
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("错误：未找到 GOOGLE_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

print("正在检查可用的模型...")
try:
    models = genai.list_models()
    print("可用的模型：")
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  支持的方法: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"检查模型时出错: {e}")

# 测试不同的模型
test_models = [
    'gemini-pro',
    'gemini-pro-vision', 
    'gemini-1.5-flash',
    'gemini-1.5-pro'
]

for model_name in test_models:
    try:
        print(f"测试模型: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✓ {model_name} 可用")
    except Exception as e:
        print(f"✗ {model_name} 不可用: {e}")
    print()