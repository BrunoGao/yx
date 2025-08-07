#!/usr/bin/env python3
"""同步分区表的org_id和user_id"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def sync_partition_org_ids():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE,
        autocommit=False
    )
    
    try:
        with conn.cursor() as cursor:
            print('🔄 同步分区表的org_id和user_id...')
            print('=' * 80)
            
            # 获取设备与用户的映射关系
            cursor.execute("""
                SELECT u.id as user_id, u.device_sn, uo.org_id
                FROM sys_user u 
                LEFT JOIN sys_user_org uo ON u.id = uo.user_id 
                WHERE u.device_sn IS NOT NULL AND u.device_sn != '' AND u.device_sn != '-'
                AND uo.org_id IS NOT NULL
            """)
            device_mappings = cursor.fetchall()
            
            print(f"找到 {len(device_mappings)} 个设备用户映射关系")
            
            # 分区表列表
            partition_tables = [
                't_user_health_data_202411',
                't_user_health_data_202412',
                't_user_health_data_202501',
                't_user_health_data_202502',
                't_user_health_data_202503',
                't_user_health_data_202504',
                't_user_health_data_202505'
            ]
            
            total_updated = 0
            
            for table in partition_tables:
                print(f"\n🔄 更新分区表 {table}...")
                
                # 检查表中缺失org_id的数据
                cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE org_id IS NULL OR user_id IS NULL')
                missing_count = cursor.fetchone()[0]
                print(f"  缺失org_id或user_id的记录: {missing_count}条")
                
                if missing_count == 0:
                    print(f"  ✅ {table} 无需更新")
                    continue
                
                table_updated = 0
                
                # 根据设备映射更新
                for user_id, device_sn, org_id in device_mappings:
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET user_id = %s, org_id = %s
                        WHERE device_sn = %s AND (user_id IS NULL OR org_id IS NULL)
                    """, (user_id, org_id, device_sn))
                    
                    affected = cursor.rowcount
                    table_updated += affected
                    
                    if affected > 0:
                        print(f"    设备 {device_sn} -> 用户ID: {user_id}, 组织ID: {org_id}, 更新: {affected}条")
                
                # 为无用户关联的设备设置默认值
                cursor.execute(f"""
                    UPDATE {table} 
                    SET user_id = 0, org_id = 1
                    WHERE user_id IS NULL OR org_id IS NULL
                """)
                default_updated = cursor.rowcount
                
                if default_updated > 0:
                    print(f"    设置默认值: {default_updated}条")
                
                table_total = table_updated + default_updated
                total_updated += table_total
                print(f"  ✅ {table} 更新完成: {table_total}条")
                
                conn.commit()
            
            print(f"\n✅ 所有分区表更新完成: 总计 {total_updated} 条记录")
            
            # 验证更新结果
            print("\n📊 验证更新结果:")
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned WHERE org_id IS NULL OR user_id IS NULL')
            remaining_null = cursor.fetchone()[0]
            print(f"  分区视图中剩余NULL的记录: {remaining_null}条")
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned WHERE org_id = 2')
            org2_count = cursor.fetchone()[0]
            print(f"  分区视图中org_id=2的记录: {org2_count}条")
            
            if remaining_null == 0:
                print("  ✅ 所有分区表org_id和user_id更新完成")
            else:
                print(f"  ❌ 仍有 {remaining_null} 条记录未更新")
                
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    sync_partition_org_ids() 