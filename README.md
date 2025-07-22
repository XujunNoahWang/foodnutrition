# 智能食物营养分析师

版本：0.1.5

一个基于AI的食物营养分析应用，可以识别食物图片并提供详细的营养信息分析。

## 功能特点

- 🍽️ **智能食物识别**: 使用Google Gemini 2.5 Flash-Lite AI识别图片中的食物
- 📊 **营养分析**: 提供嘌呤、胆固醇、饱和脂肪、糖分、热量、蛋白质等营养信息
- 🎯 **健康建议**: 根据营养数据提供个性化的健康建议
- 📱 **现代化UI**: 响应式设计，支持暗色/亮色主题切换
- 🔄 **实时分析**: 快速分析，即时显示结果
- 🗃️ **权威数据**: 基于权威嘌呤数据库进行精确分析

## 技术栈

- **后端**: Python Flask
- **AI模型**: Google Gemini 2.5 Flash-Lite Preview 06-17
- **前端**: HTML5, CSS3, JavaScript (Vanilla)
- **数据**: 权威嘌呤数据库 (purinefoods.json)

## 安装说明

### 环境要求

- Python 3.8+
- Google Gemini API Key

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/XujunNoahWang/foodnutrition.git
cd foodnutrition
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 创建 .env 文件并添加你的 Google API Key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

## 使用方法

### 快速启动

使用一键启动脚本：
```bash
python start_app.py
```

应用将自动启动并打开浏览器。

### 手动启动

1. 启动后端服务
```bash
python app.py
```

2. 访问应用
- 应用地址: http://localhost:5000

## 项目结构

```
foodnutrition/
├── app.py                 # Flask后端应用
├── start_app.py           # 一键启动脚本
├── setup.py               # 项目设置脚本
├── requirements.txt       # Python依赖
├── .env                   # 环境变量配置
├── purinefoods.json       # 权威嘌呤数据库
├── static/                # 前端静态文件
│   ├── index.html         # 主页面
│   ├── script.js          # JavaScript逻辑
│   └── style.css          # 样式文件
├── .gitignore             # Git忽略文件
└── README.md              # 项目文档
```

## API接口

### POST /analyze

分析上传的食物图片

**请求参数:**
- `image`: 图片文件 (multipart/form-data)

**响应格式:**
```json
{
  "success": true,
  "nutrition_data": {
    "foods": [
      {
        "name": "食物名称",
        "purine": {"value": 75, "unit": "mg", "level": "medium", "emoji": "🟡"},
        "cholesterol": {"value": 50, "unit": "mg", "level": "medium", "emoji": "🟡"},
        "saturated_fat": {"value": 3, "unit": "g", "level": "medium", "emoji": "🟡"},
        "sugar": {"value": 8, "unit": "g", "level": "medium", "emoji": "🟡"},
        "calories": {"value": 200, "unit": "kcal", "level": "medium", "emoji": "🟡"},
        "protein": {"value": 15, "unit": "g", "level": "medium", "emoji": "🟡"}
      }
    ],
    "suggestions": ["健康建议1", "健康建议2"]
  }
}
```

## 开发说明

### 环境配置

1. 获取Google Gemini API Key
   - 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 创建新的API Key

2. 配置环境变量
   - 创建 `.env` 文件
   - 填入你的API Key: `GOOGLE_API_KEY=your_api_key_here`

### 本地开发

1. 安装开发依赖
```bash
pip install -r requirements.txt
```

2. 启动开发服务器
```bash
python app.py
```

3. 访问 http://localhost:5000

## 依赖包

- Flask: Web框架
- flask-cors: 跨域支持
- Pillow: 图像处理
- python-dotenv: 环境变量管理
- google-generativeai: Google AI API客户端
- psutil: 系统监控

## 版本历史

- v0.1.5：升级到Gemini 2.5 Flash-Lite Preview模型，优化项目结构
- v0.1.2：优化表格字体层级与视觉层次
- v0.1.1：Restructure project to follow Python best practices
- v0.1.0：Food Nutrition Analysis App with improved startup script

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

MIT License

## 联系方式

如有问题，请通过GitHub Issues联系。 