import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv
import difflib

# 确保从正确的路径加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)

# 获取 API Key 并添加调试信息
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("错误：未找到 GOOGLE_API_KEY 环境变量")
    print(f"当前工作目录：{os.getcwd()}")
    print(f".env 文件路径：{env_path}")
    print(f".env 文件是否存在：{os.path.exists(env_path)}")
else:
    print(f"成功加载 API Key：{api_key[:10]}...")

genai.configure(api_key=api_key)
# 使用最新的 Gemini 1.5 Flash 模型，支持图像和文本
model = genai.GenerativeModel('gemini-1.5-flash')

# 加载权威嘌呤数据
def load_purine_data():
    try:
        # purinefoods.json 在项目根目录下，需要向上一级目录查找
        purine_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'purinefoods.json')
        with open(purine_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载嘌呤数据失败: {e}")
        print(f"尝试的文件路径: {purine_file_path}")
        return []

purine_data = load_purine_data()

def find_purine_value(food_name):
    """根据食物名称查找权威嘌呤含量"""
    if not purine_data:
        return None
    
    # 直接匹配
    for item in purine_data:
        if food_name in item.get('食品名', '') or item.get('食品名', '') in food_name:
            return item.get('嘌呤含量_mg_per_100g', None)
    
    # 模糊匹配
    food_names = [item.get('食品名', '') for item in purine_data]
    matches = difflib.get_close_matches(food_name, food_names, n=1, cutoff=0.6)
    
    if matches:
        for item in purine_data:
            if item.get('食品名', '') == matches[0]:
                return item.get('嘌呤含量_mg_per_100g', None)
    
    return None

def get_nutrition_level_emoji(level):
    """根据营养等级返回对应的emoji"""
    emoji_map = {
        'high': '🔴',
        'medium': '🟡', 
        'low': '🟢'
    }
    return emoji_map.get(level, '⚪')

def get_protein_level_emoji(level):
    """蛋白质使用特殊的emoji映射"""
    emoji_map = {
        'high': '🟢',  # 高蛋白是好的
        'medium': '🟡',
        'low': '⚠️'   # 低蛋白需要注意
    }
    return emoji_map.get(level, '⚪')

@app.route('/analyze', methods=['POST'])
def analyze_food():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected image file"}), 400

    try:
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))

        prompt_text = """
请识别图片中的所有食物，并以每100克可食部计，为每种食物提供以下6项营养信息：嘌呤（mg）、胆固醇（mg）、饱和脂肪（g）、糖（g）、热量（kcal）、蛋白质（g）。

请严格按照以下JSON格式返回数据：

{
  "foods": [
    {
      "name": "食物名称",
      "purine": {"value": 数值, "unit": "mg", "level": "high/medium/low"},
      "cholesterol": {"value": 数值, "unit": "mg", "level": "high/medium/low"},
      "saturated_fat": {"value": 数值, "unit": "g", "level": "high/medium/low"},
      "sugar": {"value": 数值, "unit": "g", "level": "high/medium/low"},
      "calories": {"value": 数值, "unit": "kcal", "level": "high/medium/low"},
      "protein": {"value": 数值, "unit": "g", "level": "high/medium/low"}
    }
  ],
  "suggestions": [
    "针对第一种食物的营养建议",
    "针对第二种食物的营养建议"
  ]
}

营养等级判断标准：
- 嘌呤：high >150mg, medium 75-150mg, low <75mg
- 蛋白质：high >20g, medium 10-20g, low <10g
- 胆固醇：high >100mg, medium 30-100mg, low <30mg
- 饱和脂肪：high >5g, medium 1-5g, low <1g
- 糖：high >15g, medium 5-15g, low <5g
- 热量：high >300kcal, medium 100-300kcal, low <100kcal

请只返回JSON数据，不要包含其他文字。
"""

        response = model.generate_content([prompt_text, img])
        response_text = response.text.strip()
        
        # 尝试解析JSON响应
        try:
            # 清理响应文本，移除可能的markdown代码块标记
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            nutrition_data = json.loads(response_text)
            
            # 为每个食物添加emoji标记并使用权威嘌呤数据
            for food in nutrition_data.get('foods', []):
                food_name = food.get('name', '')
                
                # 检查是否有权威嘌呤数据
                authoritative_purine = find_purine_value(food_name)
                if authoritative_purine is not None:
                    # 使用权威数据替换嘌呤值
                    if authoritative_purine > 150:
                        level = 'high'
                    elif authoritative_purine >= 75:
                        level = 'medium'
                    else:
                        level = 'low'
                    
                    food['purine'] = {
                        'value': authoritative_purine,
                        'unit': 'mg',
                        'level': level,
                        'source': 'authoritative'
                    }
                    print(f"使用权威数据：{food_name} 嘌呤含量 {authoritative_purine}mg")
                
                # 为所有营养素添加emoji
                for nutrient in ['purine', 'cholesterol', 'saturated_fat', 'sugar', 'calories']:
                    if nutrient in food:
                        level = food[nutrient].get('level', 'medium')
                        food[nutrient]['emoji'] = get_nutrition_level_emoji(level)
                
                # 蛋白质使用特殊处理
                if 'protein' in food:
                    level = food['protein'].get('level', 'medium')
                    food['protein']['emoji'] = get_protein_level_emoji(level)
            
            # 处理详细建议
            suggestions = nutrition_data.get('detailed_suggestions', nutrition_data.get('suggestions', []))
            nutrition_data['suggestions'] = suggestions
            
            return jsonify({
                "success": True,
                "nutrition_data": nutrition_data
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response_text}")
            
            # 如果JSON解析失败，尝试解析原始的markdown表格格式作为备用
            return parse_markdown_fallback(response_text)
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}), 500

def parse_markdown_fallback(response_text):
    """备用方案：解析markdown格式的响应"""
    try:
        # 简单的备用数据
        fallback_data = {
            "foods": [
                {
                    "name": "识别的食物",
                    "purine": {"value": 75, "unit": "mg", "level": "medium", "emoji": "🟡"},
                    "cholesterol": {"value": 50, "unit": "mg", "level": "medium", "emoji": "🟡"},
                    "saturated_fat": {"value": 3, "unit": "g", "level": "medium", "emoji": "🟡"},
                    "sugar": {"value": 8, "unit": "g", "level": "medium", "emoji": "🟡"},
                    "calories": {"value": 200, "unit": "kcal", "level": "medium", "emoji": "🟡"},
                    "protein": {"value": 15, "unit": "g", "level": "medium", "emoji": "🟡"}
                }
            ],
            "suggestions": [
                "AI响应格式异常，显示的是示例数据。请重新尝试分析。",
                f"原始AI响应：{response_text[:200]}..."
            ]
        }
        
        return jsonify({
            "success": True,
            "nutrition_data": fallback_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"数据解析失败: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)