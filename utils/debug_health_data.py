#!/usr/bin/env python3 #调试健康数据格式
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_cleanup_and_generator import DataCleanupAndGenerator
import json,requests

# 创建生成器实例
gen = DataCleanupAndGenerator()

# 生成一个测试健康数据
test_data = gen.generate_health_data("A5GTQ24B26000001", "测试用户")
print("生成的健康数据:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))

# 创建完整的payload
payload = {'data': test_data}
print("\n完整的payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

# 测试API调用
try:
    response = requests.post("http://localhost:5001/upload_health_data", json=payload, timeout=5)
    print(f"\nAPI响应状态码: {response.status_code}")
    print(f"API响应内容: {response.text}")
    if response.status_code != 200:
        print(f"响应头: {dict(response.headers)}")
except Exception as e:
    print(f"\n❌ API调用异常: {e}") 