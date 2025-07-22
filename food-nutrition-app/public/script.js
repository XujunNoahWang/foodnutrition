document.addEventListener('DOMContentLoaded', () => {
    // 获取DOM元素
    const themeToggle = document.getElementById('themeToggle');
    const imageUpload = document.getElementById('imageUpload');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPage = document.getElementById('uploadPage');
    const analysisPage = document.getElementById('analysisPage');
    const analysisImage = document.getElementById('analysisImage');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingState = document.getElementById('loadingState');
    const analysisResults = document.getElementById('analysisResults');
    const errorState = document.getElementById('errorState');
    const nutritionTableBody = document.getElementById('nutritionTableBody');
    const nutritionSuggestions = document.getElementById('nutritionSuggestions');
    const errorMessage = document.getElementById('errorMessage');
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    const shareBtn = document.getElementById('shareBtn');
    const retryBtn = document.getElementById('retryBtn');
    const audienceSelector = document.getElementById('audienceSelector');
    // Tab logic for nutrition suggestions
    const suggestionTabs = document.getElementById('suggestionTabs');
    let currentTab = 'general';
    let lastNutritionData = null;

    let selectedFile = null;

    // 初始化
    initEventListeners();
    initTheme();

    function initEventListeners() {
        // 主题切换
        themeToggle.addEventListener('click', toggleTheme);
        // 上传相关（不再用JS触发input.click）
        // uploadBtn和uploadArea只做拖拽，不做点击触发input
        imageUpload.addEventListener('change', handleFileSelect);
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); handleDragOver(e); });
        uploadArea.addEventListener('dragleave', (e) => { e.preventDefault(); e.stopPropagation(); handleDragLeave(e); });
        uploadArea.addEventListener('drop', (e) => { e.preventDefault(); e.stopPropagation(); handleDrop(e); });
        // 更换图片
        changeImageBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); imageUpload.click(); });
        // 操作按钮
        newAnalysisBtn.addEventListener('click', resetToUpload);
        shareBtn.addEventListener('click', shareResults);
        retryBtn.addEventListener('click', analyzeImage);
        // Tab切换监听
        if (suggestionTabs) {
            suggestionTabs.addEventListener('click', handleTabClick);
        }
    }

    // Handle tab click event
    function handleTabClick(e) {
        if (e.target.classList.contains('tab-btn')) {
            const tab = e.target.getAttribute('data-tab');
            if (tab !== currentTab) {
                currentTab = tab;
                updateTabActive();
                if (lastNutritionData) {
                    renderSuggestionsByTab(lastNutritionData);
                }
            }
        }
    }

    // Update tab active style
    function updateTabActive() {
        if (!suggestionTabs) return;
        const btns = suggestionTabs.querySelectorAll('.tab-btn');
        btns.forEach(btn => {
            if (btn.getAttribute('data-tab') === currentTab) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Render suggestions based on selected tab
    function renderSuggestionsByTab(nutritionData) {
        // 默认第一个Tab为active
        if (!currentTab || !focusKeys.includes(currentTab)) currentTab = 'cholesterol';
        updateTabActive();
        getTargetedSuggestions(currentTab, nutritionData).then(suggestions => {
            renderTargetedSuggestions(suggestions, currentTab);
        });
    }

    // 所有人群key
    const focusKeys = ['cholesterol', 'fat_loss', 'muscle_gain', 'diabetes', 'children', 'elderly', 'pregnant'];
    // 各人群关注点描述
    const focusDesc = {
        cholesterol: '胆固醇、饱和脂肪，推荐膳食纤维、蛋白质',
        fat_loss: '热量、脂肪、糖，推荐蛋白质、膳食纤维',
        muscle_gain: '蛋白质、热量，适量碳水',
        diabetes: '糖、热量，推荐膳食纤维',
        children: '蛋白质、钙，适量糖和脂肪',
        elderly: '蛋白质、膳食纤维，限制脂肪、胆固醇',
        pregnant: '蛋白质、铁、钙，限制高糖高脂'
    };
    // 针对性建议算法（判定标准更细化）
    function getTargetedSuggestions(audience, nutritionData) {
        return new Promise(resolve => {
            const foods = nutritionData.foods || [];
            // 关注点配置（更细化）
            const focus = {
                cholesterol: { more: ['fiber', 'protein'], limit: ['calories'], less: ['cholesterol', 'saturated_fat'], strict: { cholesterol: 'medium', saturated_fat: 'medium' } },
                fat_loss: { more: ['protein', 'fiber'], limit: ['calories', 'sugar'], less: ['fat', 'saturated_fat', 'sugar'], strict: { calories: 'medium', sugar: 'medium', fat: 'medium' } },
                muscle_gain: { more: ['protein', 'calories'], limit: ['sugar'], less: ['fat', 'saturated_fat'] },
                diabetes: { more: ['fiber'], limit: ['sugar', 'calories'], less: ['sugar'] },
                children: { more: ['protein', 'calcium'], limit: ['sugar'], less: ['fat', 'saturated_fat'] },
                elderly: { more: ['protein', 'fiber'], limit: ['calories', 'sugar'], less: ['fat', 'saturated_fat', 'cholesterol'] },
                pregnant: { more: ['protein', 'iron', 'calcium'], limit: ['sugar', 'fat'], less: ['saturated_fat', 'cholesterol'] }
            };
            const conf = focus[audience] || focus.cholesterol;
            const more = [], limit = [], less = [];
            foods.forEach(food => {
                let reasons = [];
                // 多吃
                conf.more && conf.more.forEach(nutrient => {
                    if (food[nutrient] && food[nutrient].level === 'low') {
                        reasons.push(`${nutrientLabel(nutrient)}低`);
                    }
                });
                if (reasons.length) {
                    more.push({ name: food.name, reasons });
                    return;
                }
                // 限量
                reasons = [];
                conf.limit && conf.limit.forEach(nutrient => {
                    if (food[nutrient] && food[nutrient].level === 'medium') {
                        reasons.push(`${nutrientLabel(nutrient)}适中`);
                    }
                });
                // 严格判定（如高胆固醇人群对胆固醇medium也限量，减脂对热量medium也限量）
                if (conf.strict) {
                    Object.entries(conf.strict).forEach(([nutrient, level]) => {
                        if (food[nutrient] && food[nutrient].level === level) {
                            reasons.push(`${nutrientLabel(nutrient)}${level === 'medium' ? '偏高' : '适中'}`);
                        }
                    });
                }
                if (reasons.length) {
                    limit.push({ name: food.name, reasons });
                    return;
                }
                // 少吃
                reasons = [];
                conf.less && conf.less.forEach(nutrient => {
                    if (food[nutrient] && food[nutrient].level === 'high') {
                        reasons.push(`${nutrientLabel(nutrient)}高`);
                    }
                });
                if (reasons.length) {
                    less.push({ name: food.name, reasons });
                }
            });
            resolve({ more, limit, less });
        });
    }
    // 营养素中文标签
    function nutrientLabel(key) {
        const map = {
            purine: '嘌呤',
            cholesterol: '胆固醇',
            saturated_fat: '饱和脂肪',
            sugar: '糖',
            calories: '热量',
            protein: '蛋白质',
            fiber: '膳食纤维',
            fat: '脂肪',
            calcium: '钙',
            iron: '铁'
        };
        return map[key] || key;
    }
    // 渲染分栏建议，顶部加人群描述
    function renderTargetedSuggestions({ more, limit, less }, audience) {
        nutritionSuggestions.innerHTML = `
            <div class="targeted-desc">本建议针对<b>${tabLabel(audience)}</b>，优先关注：${focusDesc[audience] || ''}</div>
            <div class="targeted-suggestion-row">
                <div class="targeted-suggestion-col">
                    <div class="targeted-title">多吃</div>
                    ${more.length ? more.map(f => `<div class='targeted-item'><b>${f.name}</b><span class='targeted-reason'>（${f.reasons.join('，')}）</span></div>`).join('') : '<div class="targeted-empty">暂无推荐</div>'}
                </div>
                <div class="targeted-suggestion-col">
                    <div class="targeted-title">限量</div>
                    ${limit.length ? limit.map(f => `<div class='targeted-item'><b>${f.name}</b><span class='targeted-reason'>（${f.reasons.join('，')}）</span></div>`).join('') : '<div class="targeted-empty">暂无推荐</div>'}
                </div>
                <div class="targeted-suggestion-col">
                    <div class="targeted-title">少吃</div>
                    ${less.length ? less.map(f => `<div class='targeted-item'><b>${f.name}</b><span class='targeted-reason'>（${f.reasons.join('，')}）</span></div>`).join('') : '<div class="targeted-empty">暂无推荐</div>'}
                </div>
            </div>
        `;
    }
    // Tab中文标签
    function tabLabel(key) {
        const map = {
            cholesterol: '高胆固醇',
            fat_loss: '减脂',
            muscle_gain: '增肌',
            diabetes: '糖尿病',
            children: '儿童',
            elderly: '老年人',
            pregnant: '孕妇'
        };
        return map[key] || key;
    }

    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    }

    function toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    }

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    function handleFileSelect(event) {
        event.preventDefault && event.preventDefault();
        try {
            const file = event.target.files[0];
            if (file && file.type.startsWith('image/')) {
                selectedFile = file;
                displayImageAndAnalyze(file);
            } else {
                showError('请选择有效的图片文件');
            }
        } catch (err) {
            alert('图片选择失败，可能是浏览器兼容性问题。' + err);
            console.error('handleFileSelect error:', err);
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            selectedFile = files[0];
            displayImageAndAnalyze(files[0]);
        } else {
            showError('请拖拽有效的图片文件');
        }
    }

    function displayImageAndAnalyze(file) {
        try {
            const reader = new FileReader();
            reader.onload = (e) => {
                analysisImage.src = e.target.result;
                showAnalysisPage();
                analyzeImage();
            };
            reader.onerror = (e) => {
                alert('图片读取失败，可能是浏览器兼容性问题。');
                console.error('FileReader error:', e);
            };
            reader.readAsDataURL(file);
        } catch (err) {
            alert('图片读取失败，可能是浏览器兼容性问题。' + err);
            console.error('displayImageAndAnalyze error:', err);
        }
    }

    function showAnalysisPage() {
        uploadPage.style.display = 'none';
        analysisPage.style.display = 'grid';
        showLoadingState();
    }

    function showLoadingState() {
        loadingState.style.display = 'flex';
        analysisResults.style.display = 'none';
        errorState.style.display = 'none';
    }

    function showResults() {
        loadingState.style.display = 'none';
        analysisResults.style.display = 'block';
        errorState.style.display = 'none';
    }

    function showError(message) {
        loadingState.style.display = 'none';
        analysisResults.style.display = 'none';
        errorState.style.display = 'flex';
        errorMessage.innerHTML = message; // 使用innerHTML处理HTML内容
    }

    async function analyzeImage() {
        if (!selectedFile) {
            showError('请先选择一张图片');
            return;
        }

        const formData = new FormData();
        formData.append('image', selectedFile);

        // 动态适配后端接口地址
        const backendHost = window.location.hostname;
        const backendUrl = `http://${backendHost}:5000/analyze`;

        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                body: formData
            });

            let errorDetail = '';
            if (!response.ok) {
                try {
                    const errorData = await response.json();
                    errorDetail = JSON.stringify(errorData, null, 2);
                    throw new Error(errorData.error || `HTTP错误: ${response.status}`);
                } catch (e) {
                    const text = await response.text();
                    errorDetail = `HTTP状态码: ${response.status}\n原始响应: ${text}`;
                    throw new Error(`HTTP错误: ${response.status}`);
                }
            }

            const data = await response.json();

            if (data.success && data.nutrition_data) {
                renderResults(data.nutrition_data);
                showResults();
            } else {
                errorDetail = JSON.stringify(data, null, 2);
                throw new Error(data.error || '分析失败');
            }

        } catch (error) {
            // 显示详细错误信息在页面上
            const errorDetailText = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail || '无详细信息', null, 2);
            showError(`${error.message}<br><pre style='white-space:pre-wrap;word-break:break-all;font-size:0.95em;color:#c00;background:#fff3f3;padding:0.5em 1em;border-radius:8px;'>${error.stack || ''}</pre><br><b>详细信息：</b><br><pre style='white-space:pre-wrap;word-break:break-all;font-size:0.95em;color:#333;background:#f7f7f7;padding:0.5em 1em;border-radius:8px;'>${errorDetailText}</pre>`);
            console.error('分析错误:', error);
        }
    }

    // Render nutrition results
    function renderResults(nutritionData) {
        renderNutritionTable(nutritionData);
        lastNutritionData = nutritionData;
        updateTabActive();
        renderSuggestionsByTab(nutritionData);
    }

    function renderNutritionTable(nutritionData) {
        nutritionTableBody.innerHTML = '';

        if (!nutritionData.foods || nutritionData.foods.length === 0) {
            nutritionTableBody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                        未识别到食物数据
                    </td>
                </tr>
            `;
            return;
        }

        nutritionData.foods.forEach((food, index) => {
            const row = document.createElement('tr');
            row.style.animationDelay = `${index * 0.1}s`;
            
            // 食物名称
            const nameCell = document.createElement('td');
            nameCell.textContent = food.name || '未知食物';
            row.appendChild(nameCell);

            // 营养数据
            const nutrients = ['purine', 'cholesterol', 'saturated_fat', 'sugar', 'calories', 'protein'];
            
            nutrients.forEach(nutrient => {
                const cell = document.createElement('td');
                const data = food[nutrient];
                
                if (data) {
                    const nutritionValue = document.createElement('div');
                    nutritionValue.className = 'nutrition-value';
                    
                    const emoji = document.createElement('span');
                    emoji.className = 'nutrition-emoji';
                    emoji.textContent = data.emoji || '⚪';
                    
                    const number = document.createElement('span');
                    number.className = 'nutrition-number';
                    number.textContent = data.value || '0';
                    
                    const unit = document.createElement('span');
                    unit.className = 'nutrition-unit';
                    unit.textContent = data.unit || '';
                    
                    nutritionValue.appendChild(emoji);
                    nutritionValue.appendChild(number);
                    nutritionValue.appendChild(unit);
                    
                    cell.appendChild(nutritionValue);
                } else {
                    cell.innerHTML = '<div class="nutrition-value"><span class="nutrition-emoji">⚪</span><span class="nutrition-number">0</span></div>';
                }
                
                row.appendChild(cell);
            });

            nutritionTableBody.appendChild(row);
        });
    }

    function renderSuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            nutritionSuggestions.innerHTML = '<p>暂无营养建议</p>';
            return;
        }

        const suggestionsHTML = suggestions
            .map(suggestion => `<p>${suggestion}</p>`)
            .join('');
        
        nutritionSuggestions.innerHTML = suggestionsHTML;
    }

    function resetToUpload() {
        selectedFile = null;
        imageUpload.value = '';
        analysisImage.src = '#';
        uploadPage.style.display = 'flex';
        analysisPage.style.display = 'none';
    }

    function shareResults() {
        if (navigator.share) {
            navigator.share({
                title: '食物营养分析结果',
                text: '查看我的食物营养分析结果',
                url: window.location.href
            }).catch(console.error);
        } else {
            // 复制到剪贴板
            const resultsText = nutritionSuggestions.textContent;
            navigator.clipboard.writeText(resultsText).then(() => {
                showNotification('结果已复制到剪贴板');
            }).catch(() => {
                showNotification('分享功能暂不可用');
            });
        }
    }

    function showNotification(message) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-blue);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius-medium);
            box-shadow: var(--shadow-medium);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            font-weight: 500;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // 3秒后移除
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // 添加CSS动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});