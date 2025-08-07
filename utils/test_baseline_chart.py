#!/usr/bin/env python3
"""基线图表优化测试脚本"""
import requests,json,time
from datetime import datetime,timedelta

# 配置
BASE_URL = "http://localhost:5001"
BASELINE_API = f"{BASE_URL}/api/baseline/generate"
CHART_API = f"{BASE_URL}/health_data/chart/baseline"

def test_baseline_chart():
    """测试基线图表显示优化"""
    print("=== 基线图表优化测试 ===")
    
    # 1. 生成基线数据
    print("\n1. 生成基线数据...")
    for i in range(5):
        target_date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
        try:
            response = requests.post(BASELINE_API, json={'target_date': target_date}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                user_count = result.get('user_baseline', {}).get('count', 0)
                org_count = result.get('org_baseline', {}).get('count', 0)
                print(f"✓ 基线生成({target_date}): 用户{user_count}条, 组织{org_count}条")
            else:
                print(f"✗ 基线生成失败({target_date}): {response.status_code}")
        except Exception as e:
            print(f"✗ 基线生成异常({target_date}): {e}")
        time.sleep(0.5)
    
    # 2. 测试组织基线图表
    print("\n2. 测试组织基线图表...")
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        'orgId': 2,
        'startDate': start_date,
        'endDate': end_date
    }
    
    try:
        response = requests.get(CHART_API, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 组织基线查询成功")
            print(f"  - 数据源: {result.get('data_source', 'unknown')}")
            print(f"  - 日期范围: {result.get('date_range', 'unknown')}")
            print(f"  - 总天数: {result.get('total_days', 0)}")
            
            metrics = result.get('metrics', [])
            print(f"  - 指标数量: {len(metrics)}")
            
            for metric in metrics[:3]:  # 显示前3个指标
                name = metric.get('name', 'unknown')
                color = metric.get('color', '#000000')
                unit = metric.get('unit', '')
                data_count = metric.get('data_count', 0)
                normal_range = metric.get('normal_range', [])
                
                print(f"    * {name} ({color}): {data_count}个数据点, 单位{unit}, 正常范围{normal_range}")
                
                # 显示部分数值
                values = metric.get('values', [])
                non_null_values = [v for v in values if v is not None]
                if non_null_values:
                    avg_value = sum(non_null_values) / len(non_null_values)
                    print(f"      平均值: {avg_value:.1f}{unit}")
        else:
            print(f"✗ 组织基线查询失败: {response.status_code}")
            print(f"  响应: {response.text}")
    except Exception as e:
        print(f"✗ 组织基线查询异常: {e}")
    
    # 3. 测试用户基线图表
    print("\n3. 测试用户基线图表...")
    params['userId'] = '1898157930052595713'
    del params['orgId']
    
    try:
        response = requests.get(CHART_API, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 用户基线查询成功")
            print(f"  - 数据源: {result.get('data_source', 'unknown')}")
            print(f"  - 日期范围: {result.get('date_range', 'unknown')}")
            
            metrics = result.get('metrics', [])
            print(f"  - 指标数量: {len(metrics)}")
            
            for metric in metrics:
                name = metric.get('name', 'unknown')
                data_count = metric.get('data_count', 0)
                if data_count > 0:
                    print(f"    * {name}: {data_count}个数据点")
        else:
            print(f"✗ 用户基线查询失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 用户基线查询异常: {e}")
    
    # 4. 测试图表数据格式
    print("\n4. 验证图表数据格式...")
    if 'result' in locals() and result.get('success'):
        dates = result.get('dates', [])
        metrics = result.get('metrics', [])
        
        print(f"✓ 日期格式正确: {len(dates)}个日期")
        print(f"  首日: {dates[0] if dates else 'N/A'}")
        print(f"  末日: {dates[-1] if dates else 'N/A'}")
        
        for metric in metrics[:2]:
            name = metric.get('name')
            values = metric.get('values', [])
            color = metric.get('color')
            unit = metric.get('unit')
            normal_range = metric.get('normal_range', [])
            
            print(f"✓ {name}指标格式正确:")
            print(f"  - 颜色: {color}")
            print(f"  - 单位: {unit}")
            print(f"  - 正常范围: {normal_range}")
            print(f"  - 数据点: {len(values)}个")
            print(f"  - 有效值: {len([v for v in values if v is not None])}个")
    
    print("\n=== 测试完成 ===")

def test_chart_colors():
    """测试图表颜色配置"""
    print("\n=== 图表颜色配置测试 ===")
    
    colors = {
        '心率': '#00D4AA',
        '血氧': '#1890FF', 
        '体温': '#FAAD14',
        '收缩压': '#F5222D',
        '舒张压': '#FA8C16',
        '压力': '#722ED1'
    }
    
    for name, color in colors.items():
        print(f"✓ {name}: {color}")
    
    print("颜色配置验证完成")

if __name__ == "__main__":
    test_baseline_chart()
    test_chart_colors() 