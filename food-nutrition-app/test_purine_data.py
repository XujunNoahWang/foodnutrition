import os
import json
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from app import load_purine_data, find_purine_value

# 测试嘌呤数据加载
print("测试权威嘌呤数据加载...")
purine_data = load_purine_data()

if purine_data:
    print(f"✅ 成功加载 {len(purine_data)} 条嘌呤数据")
    
    # 测试几个常见食物
    test_foods = ['大米', '鸡肉', '猪肝', '豆腐', '菠菜']
    
    print("\n测试食物嘌呤含量查找:")
    for food in test_foods:
        purine_value = find_purine_value(food)
        if purine_value is not None:
            print(f"✅ {food}: {purine_value}mg/100g")
        else:
            print(f"❌ {food}: 未找到数据")
    
    # 显示前5条数据作为示例
    print(f"\n前5条数据示例:")
    for i, item in enumerate(purine_data[:5]):
        print(f"{i+1}. {item.get('食品名', 'N/A')}: {item.get('嘌呤含量_mg_per_100g', 'N/A')}mg/100g")
        
else:
    print("❌ 嘌呤数据加载失败")