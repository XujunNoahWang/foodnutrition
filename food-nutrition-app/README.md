# 食物营养分析助手 (Food Nutrition Analyzer)

基于 Google Gemini API 的图片食物识别与营养分析 Web 应用。

## 功能简介
- 上传食物图片，自动识别图片中的食物种类。
- 获取每100克可食部的嘌呤、胆固醇、饱和脂肪、糖、热量、蛋白质等营养信息。
- 后端根据阈值为营养指标添加颜色 Emoji 标记。
- 前端以结构化表格和建议形式展示分析结果。
- 无需数据库，所有数据依赖 Gemini API。

## 技术栈
- 后端：Python, Flask, google-generativeai, Pillow, python-dotenv
- 前端：HTML, CSS, JavaScript, [marked.js](https://github.com/markedjs/marked)

## 目录结构
```
food-nutrition-app/
├── .env                  # 存放 GOOGLE_API_KEY
├── app.py                # Python Flask 后端代码
├── requirements.txt      # Python 依赖
├── start_app.py          # 一键启动脚本
├── public/
│   ├── index.html        # 前端主页面
│   ├── style.css         # 前端样式
│   └── script.js         # 前端 JavaScript 逻辑
└── README.md             # 项目说明
```

## 一键启动方式（推荐）
1. **配置 Google Gemini API Key**
   - 在 `food-nutrition-app/` 目录下创建 `.env` 文件：
     ```
     GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
     ```
   - 替换为你的实际 API Key。

2. **安装 Python 依赖**
   ```bash
   cd food-nutrition-app
   pip install -r requirements.txt
   ```

3. **一键启动应用**
   ```bash
   python start_app.py
   ```
   - 程序会自动启动后端和前端静态服务器，并自动打开浏览器页面。

4. **使用方法**
   - 上传图片，点击“分析营养”，即可查看结果。

## 手动启动方式
如遇特殊需求，也可手动分别启动后端和前端：

- 后端：
  ```bash
  python app.py
  ```
- 前端（静态服务器）：
  ```bash
  cd public
  python -m http.server 8080
  ```
- 浏览器访问：http://127.0.0.1:8080

## 注意事项
- 后端需联网，且 API Key 有效。
- 前端通过 fetch 访问本地后端 API，若端口或地址有变请同步修改。
- 仅供学习与个人用途。 