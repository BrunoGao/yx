#!/usr/bin/env python3 #测试设备信息更新
from data_cleanup_and_generator import DataCleanupAndGenerator

def test_device_update():
    gen = DataCleanupAndGenerator()
    
    if not gen.connect_db():
        return
    
    try:
        # 检查现有设备
        gen.cursor.execute("SELECT serial_number, user_id, org_id FROM t_device_info LIMIT 3")
        devices = gen.cursor.fetchall()
        
        if not devices:
            print("❌ 没有找到设备数据")
            return
            
        print("🔍 现有设备信息:")
        for device in devices:
            print(f"  设备: {device['serial_number']}, 用户ID: {device['user_id']}, 组织ID: {device['org_id']}")
        
        # 测试更新第一个设备
        test_device = devices[0]
        test_serial = test_device['serial_number']
        
        print(f"\n🧪 测试更新设备 {test_serial}...")
        
        # 模拟用户和组织ID
        test_user_id = 12345
        test_org_id = 67890
        
        # 更新设备信息
        if gen.update_device_info(test_serial, test_user_id, test_org_id):
            print("✅ 设备信息更新成功")
            
            # 验证更新结果
            gen.cursor.execute("SELECT serial_number, user_id, org_id FROM t_device_info WHERE serial_number = %s", (test_serial,))
            updated_device = gen.cursor.fetchone()
            
            if updated_device:
                print(f"✅ 验证结果:")
                print(f"  设备: {updated_device['serial_number']}")
                print(f"  用户ID: {updated_device['user_id']} (期望: {test_user_id})")
                print(f"  组织ID: {updated_device['org_id']} (期望: {test_org_id})")
                
                if updated_device['user_id'] == test_user_id and updated_device['org_id'] == test_org_id:
                    print("🎉 设备信息更新测试通过！")
                else:
                    print("❌ 设备信息更新验证失败")
            else:
                print("❌ 无法查询到更新后的设备信息")
        else:
            print("❌ 设备信息更新失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        if gen.conn:
            gen.conn.close()

if __name__ == "__main__":
    test_device_update() 