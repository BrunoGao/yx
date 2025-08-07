#!/usr/bin/env python3
"""
测试基线API问题的调试脚本
"""
import sys
import os
sys.path.append('/Users/bg/work/codes/springboot/ljwx/flt/ljwx-bigscreen/bigscreen')

from flask import Flask
from datetime import datetime, timedelta
import traceback

# 创建Flask应用上下文
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 导入数据库模型
from bigScreen.models import db, OrgHealthBaseline
from sqlalchemy import and_

# 初始化数据库
db.init_app(app)

def test_baseline_access():
    """测试基线数据访问"""
    try:
        with app.app_context():
            # 设置参数
            orgId = '1939964806110937090'
            days = 7
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            print(f"🔍 查询参数:")
            print(f"   orgId: {orgId}")
            print(f"   start_date: {start_date}")
            print(f"   end_date: {end_date}")
            
            # 查询组织基线数据
            baselines = db.session.query(OrgHealthBaseline).filter(
                and_(
                    OrgHealthBaseline.org_id == orgId,
                    OrgHealthBaseline.baseline_date >= start_date,
                    OrgHealthBaseline.baseline_date <= end_date
                )
            ).order_by(OrgHealthBaseline.baseline_date, OrgHealthBaseline.feature_name).all()
            
            print(f"📊 查询到 {len(baselines)} 条基线记录")
            
            if baselines:
                print(f"📝 测试第一条记录属性访问:")
                baseline = baselines[0]
                print(f"   ID: {baseline.id}")
                print(f"   feature_name: {baseline.feature_name}")
                print(f"   baseline_date: {baseline.baseline_date}")
                
                # 测试访问不同的属性名
                print(f"🧪 测试属性访问:")
                try:
                    mean_value = baseline.mean_value
                    print(f"   ✅ baseline.mean_value: {mean_value}")
                except AttributeError as e:
                    print(f"   ❌ baseline.mean_value error: {e}")
                
                try:
                    baseline_value = baseline.baseline_value
                    print(f"   ✅ baseline.baseline_value: {baseline_value}")
                except AttributeError as e:
                    print(f"   ❌ baseline.baseline_value error: {e}")
                
                # 打印所有可用属性
                print(f"🔍 所有可用属性:")
                for attr in sorted(dir(baseline)):  
                    if not attr.startswith('_') and not callable(getattr(baseline, attr)):
                        value = getattr(baseline, attr)
                        print(f"   {attr}: {value}")
                        
            else:
                print("❌ 未查询到任何基线数据")
            
            return {'success': True, 'count': len(baselines)}
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 基线API属性访问测试")
    print("=" * 50)
    
    result = test_baseline_access()
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {result}")
    print("=" * 50)