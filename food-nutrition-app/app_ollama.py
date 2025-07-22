import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from dotenv import load_dotenv
import requests
import json

# 确保从正确的路径加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)

# Ollama 本地 API 设置
OLLAMA_URL = "http://localhost:11434/api/generate"

def check_ollama_available():
    """检查 Ollama 是否可用"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

def analyze_with_ollama(image_base64, prompt):
    """使用 Ollama 分析图像"""
    payload = {
        "model": "llava",  # 支持图像的模型
        "prompt": prompt,
        "images": [image_base64],
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama API 错误: {response.text}")

@app.route('/analyze', methods=['POST'])
def analyze_food():
    if not check_ollama_available():
        return jsonify({
            "error": "Ollama 服务未运行。请先安装并启动 Ollama，然后运行 'ollama pull llava' 下载视觉模型。"
        }), 500

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
        
        # 转换为 JPEG 并编码为 base64
        img_buffer = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(img_buffer, format="JPEG", quality=85)
        img_buffer.seek(0)
        
        image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        prompt = """请识别图片中的所有食物，并以每100克可食部计，为每种食物提供以下6项营养信息：嘌呤（mg）、胆固醇（mg）、饱和脂肪（g）、糖（g）、热量（kcal）、蛋白质（g）。

请严格按照以下Markdown表格格式输出营养信息，并在数值前使用颜色Emoji标记（🔴 高/危险, 🟡 中等/较高, 🟢 低/安全/优, ⚠️ 偏低），单位统一为每100克可食部。

颜色标记规则：
- 嘌呤：🔴 >150 mg, 🟡 75–150 mg, 🟢 <75 mg
- 蛋白质：🟢 >20g, 🟡 10–20g, ⚠️ <10g
- 胆固醇：🔴 >100 mg, 🟡 30-100 mg, 🟢 <30 mg
- 饱和脂肪：🔴 >5 g, 🟡 1-5 g, 🟢 <1 g
- 糖：🔴 >15 g, 🟡 5-15 g, 🟢 <5 g
- 热量：🔴 >300 kcal, 🟡 100-300 kcal, 🟢 <100 kcal

表格示例：
| 食物    | 嘌呤     | 胆固醇    | 饱和脂肪 | 糖      | 热量    | 蛋白质  |
|---------|----------|-----------|----------|---------|---------|---------|
| 汉堡    | 🔴 138mg | 🔴 60mg   | 🔴 5.3g  | 🟡 5.6g | 🔴 260kcal | 🟡 12g  |

在表格下方，请使用`---`作为分隔符，然后提供营养建议。"""

        # 使用 Ollama 分析
        print("正在使用 Ollama 本地模型分析图像...")
        response_text = analyze_with_ollama(image_base64, prompt)
        
        # 解析响应
        parts = response_text.split('---', 1)
        table_markdown = ""
        suggestions_text = ""
        if len(parts) > 1:
            table_markdown = parts[0].strip()
            suggestions_text = parts[1].strip()
        else:
            if response_text.strip().startswith('|'):
                table_markdown = response_text.strip()
                suggestions_text = "基于本地 AI 模型的分析结果，请参考专业营养数据。"
            else:
                suggestions_text = response_text.strip()
                table_markdown = "未检测到营养表格信息。"

        return jsonify({
            "success": True,
            "table_markdown": table_markdown,
            "suggestions_text": suggestions_text + "\n\n注意：此结果由本地 Ollama 模型生成，完全免费使用。"
        })
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True, port=5003)