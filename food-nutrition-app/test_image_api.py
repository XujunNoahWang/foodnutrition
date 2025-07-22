import os
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("错误：未找到 GOOGLE_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

# 创建一个简单的测试图像
def create_test_image():
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill='red')
    draw.text((75, 75), "TEST", fill='black')
    return img

print("测试图像分析功能...")

# 测试不同的模型
models_to_test = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro-vision'
]

test_image = create_test_image()

for model_name in models_to_test:
    try:
        print(f"\n测试模型: {model_name}")
        model = genai.GenerativeModel(model_name)
        
        # 简单的图像描述测试
        response = model.generate_content([
            "请描述这张图片中看到了什么？", 
            test_image
        ])
        
        print(f"✓ {model_name} 图像分析可用")
        print(f"响应: {response.text[:100]}...")
        
    except Exception as e:
        print(f"✗ {model_name} 图像分析不可用: {e}")

print("\n测试完成！")