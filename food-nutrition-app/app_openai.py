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

# 获取 OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("错误：未找到 OPENAI_API_KEY 环境变量")
    print("请在 .env 文件中添加: OPENAI_API_KEY=your_openai_api_key")
else:
    print(f"成功加载 OpenAI API Key：{openai_api_key[:10]}...")

def encode_image(image_bytes):
    """将图片编码为 base64"""
    return base64.b64encode(image_bytes).decode('utf-8')

@app.route('/analyze', methods=['POST'])
def analyze_food():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected image file"}), 400

    try:
        image_bytes = image_file.read()
        
        # 压缩图片以减少 API 调用成本
        img = Image.open(io.BytesIO(image_bytes))
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # 转换为 JPEG 格式
        img_buffer = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(img_buffer, format="JPEG", quality=85)
        img_buffer.seek(0)
        
        # 编码图片
        base64_image = encode_image(img_buffer.getvalue())

        prompt_text = """
请识别图片中的所有食物，并以每100克可食部计，为每种食物提供以下6项营养信息：嘌呤（mg）、胆固醇（mg）、饱和脂肪（g）、糖（g）、热量（kcal）、蛋白质（g）。

请严格按照以下Markdown表格格式输出营养信息，并在数值前使用颜色Emoji标记（🔴 高/危险, 🟡 中等/较高, 🟢 低/安全/优, ⚠️ 偏低），单位统一为每100克可食部。

颜色标记规则：
- 嘌呤：🔴 >150 mg, 🟡 75–150 mg, 🟢 <75 mg (其中 <30 mg 为安全)
- 蛋白质：🟢 >20g, 🟡 10–20g, ⚠️ <10g
- 胆固醇：🔴 >100 mg, 🟡 30-100 mg, 🟢 <30 mg
- 饱和脂肪：🔴 >5 g, 🟡 1-5 g, 🟢 <1 g
- 糖：🔴 >15 g, 🟡 5-15 g, 🟢 <5 g
- 热量：🔴 >300 kcal, 🟡 100-300 kcal, 🟢 <100 kcal

表格示例：
| 食物    | 嘌呤     | 胆固醇    | 饱和脂肪 | 糖      | 热量    | 蛋白质  |
|---------|----------|-----------|----------|---------|---------|---------|
| 汉堡    | 🔴 138mg | 🔴 60mg   | 🔴 5.3g  | 🟡 5.6g | 🔴 260kcal | 🟡 12g  |
| 薯条    | 🟢 13mg  | 🟢 0mg    | 🟡 2.3g  | 🟢 0.3g | 🔴 312kcal | ⚠️ 3g   |

在表格下方，请使用`---`作为分隔符，然后为每种识别出的食物提供一段简洁的营养建议。例如：
- "嘌呤偏高但蛋白质丰富，痛风人群不宜食用，普通人适量即可"
- "整体营养良好，低糖低脂，适合健康饮食"
- "热量高、胆固醇高，应控制摄入频率"

如果图片模糊或识别不确定，请在建议部分注明"以下食物识别不确定"。
"""

        # 调用 OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        payload = {
            "model": "gpt-4o",  # 使用 GPT-4o 模型，支持图像
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=payload)
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"OpenAI API 错误: {error_data.get('error', {}).get('message', 'Unknown error')}")

        result = response.json()
        response_text = result['choices'][0]['message']['content']

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
                suggestions_text = "未检测到具体建议，请根据表格信息自行判断。"
            else:
                suggestions_text = response_text.strip()
                table_markdown = "未检测到营养表格信息。"

        return jsonify({
            "success": True,
            "table_markdown": table_markdown,
            "suggestions_text": suggestions_text
        })
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 使用不同端口避免冲突