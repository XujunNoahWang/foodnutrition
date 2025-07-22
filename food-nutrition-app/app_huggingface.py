import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from dotenv import load_dotenv
import requests

# 确保从正确的路径加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)

# Hugging Face API 设置
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
hf_token = os.getenv("HUGGINGFACE_API_TOKEN")

if not hf_token:
    print("警告：未找到 HUGGINGFACE_API_TOKEN，将使用免费限制版本")
    print("你可以在 https://huggingface.co/settings/tokens 获取免费 token")
else:
    print(f"成功加载 Hugging Face Token：{hf_token[:10]}...")

def analyze_image_with_hf(image_bytes):
    """使用 Hugging Face 分析图像"""
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    response = requests.post(HF_API_URL, headers=headers, data=image_bytes)
    return response.json()

def generate_nutrition_data(food_description):
    """基于食物描述生成营养数据（模拟数据，仅供学习）"""
    # 这里是模拟的营养数据，实际应用中需要连接营养数据库
    food_nutrition_db = {
        "burger": {"嘌呤": "🔴 138mg", "胆固醇": "🔴 60mg", "饱和脂肪": "🔴 5.3g", "糖": "🟡 5.6g", "热量": "🔴 260kcal", "蛋白质": "🟡 12g"},
        "pizza": {"嘌呤": "🟡 85mg", "胆固醇": "🟡 45mg", "饱和脂肪": "🔴 6.2g", "糖": "🟡 8.1g", "热量": "🔴 285kcal", "蛋白质": "🟡 11g"},
        "salad": {"嘌呤": "🟢 25mg", "胆固醇": "🟢 5mg", "饱和脂肪": "🟢 0.8g", "糖": "🟢 3.2g", "热量": "🟢 45kcal", "蛋白质": "⚠️ 3g"},
        "chicken": {"嘌呤": "🟡 120mg", "胆固醇": "🟡 85mg", "饱和脂肪": "🟡 2.8g", "糖": "🟢 0g", "热量": "🟡 165kcal", "蛋白质": "🟢 31g"},
        "rice": {"嘌呤": "🟢 35mg", "胆固醇": "🟢 0mg", "饱和脂肪": "🟢 0.2g", "糖": "🟢 0.1g", "热量": "🟡 130kcal", "蛋白质": "⚠️ 2.7g"},
        "bread": {"嘌呤": "🟢 45mg", "胆固醇": "🟢 0mg", "饱和脂肪": "🟢 0.6g", "糖": "🟡 5.2g", "热量": "🟡 265kcal", "蛋白质": "⚠️ 9g"},
        "fish": {"嘌呤": "🔴 180mg", "胆固醇": "🟡 55mg", "饱和脂肪": "🟢 0.9g", "糖": "🟢 0g", "热量": "🟡 145kcal", "蛋白质": "🟢 28g"},
        "apple": {"嘌呤": "🟢 15mg", "胆固醇": "🟢 0mg", "饱和脂肪": "🟢 0.1g", "糖": "🟡 10.4g", "热量": "🟢 52kcal", "蛋白质": "⚠️ 0.3g"},
        "default": {"嘌呤": "🟡 75mg", "胆固醇": "🟡 30mg", "饱和脂肪": "🟡 2.5g", "糖": "🟡 8g", "热量": "🟡 150kcal", "蛋白质": "🟡 10g"}
    }
    
    # 简单的关键词匹配
    description_lower = food_description.lower()
    for food_key in food_nutrition_db:
        if food_key in description_lower:
            return food_key, food_nutrition_db[food_key]
    
    return "未知食物", food_nutrition_db["default"]

@app.route('/analyze', methods=['POST'])
def analyze_food():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected image file"}), 400

    try:
        image_bytes = image_file.read()
        
        # 压缩图片
        img = Image.open(io.BytesIO(image_bytes))
        if img.width > 512 or img.height > 512:
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        
        # 转换为 JPEG
        img_buffer = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(img_buffer, format="JPEG", quality=85)
        img_buffer.seek(0)
        
        # 使用 Hugging Face 分析图像
        print("正在使用 Hugging Face 分析图像...")
        hf_result = analyze_image_with_hf(img_buffer.getvalue())
        
        if isinstance(hf_result, list) and len(hf_result) > 0:
            food_description = hf_result[0].get('generated_text', '未知食物')
        else:
            food_description = "未知食物"
        
        print(f"图像识别结果: {food_description}")
        
        # 生成营养数据
        food_name, nutrition_data = generate_nutrition_data(food_description)
        
        # 构建表格
        table_markdown = f"""| 食物 | 嘌呤 | 胆固醇 | 饱和脂肪 | 糖 | 热量 | 蛋白质 |
|------|------|--------|----------|----|----- |--------|
| {food_name} | {nutrition_data['嘌呤']} | {nutrition_data['胆固醇']} | {nutrition_data['饱和脂肪']} | {nutrition_data['糖']} | {nutrition_data['热量']} | {nutrition_data['蛋白质']} |"""

        # 生成建议
        suggestions_text = f"""基于图像识别结果：{food_description}

营养建议：
- 这是基于免费 AI 模型的演示版本，营养数据为模拟数据
- 实际营养值可能有所不同，请参考专业营养数据库
- 建议均衡饮食，适量摄入各类营养素
- 如有特殊健康需求，请咨询营养师或医生

注意：此为学习演示版本，使用了 Hugging Face 免费 API 进行图像识别"""

        return jsonify({
            "success": True,
            "table_markdown": table_markdown,
            "suggestions_text": suggestions_text
        })
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": f"分析失败: {str(e)}"}, 500)

if __name__ == '__main__':
    app.run(debug=True, port=5002)