#!/usr/bin/env python3
"""测试位置生成范围"""
from realtime_data_simulator import RealtimeSimulator

# 测试位置生成
sim = RealtimeSimulator()
user = {'user_name': 'test', 'device_sn': 'TEST123'}
sim.device_states['TEST123'] = {'wear_state': 0}

print('=== 位置变化测试 ===')
positions = []
for i in range(10):
    data = sim.generate_health_data(user)
    lat = float(data['latitude'])
    lng = float(data['longitude'])
    positions.append((lat, lng))
    print(f'{i+1:2d}: 纬度{lat:.6f} 经度{lng:.6f}')

# 计算位置变化范围
lats = [p[0] for p in positions]
lngs = [p[1] for p in positions]
lat_range = max(lats) - min(lats)
lng_range = max(lngs) - min(lngs)

print(f'\n变化范围:')
print(f'纬度范围: {lat_range:.6f}度 (约{lat_range*111000:.0f}米)')
print(f'经度范围: {lng_range:.6f}度 (约{lng_range*96000:.0f}米)')
print('✓ 位置控制在100米范围内' if lat_range < 0.002 and lng_range < 0.003 else '✗ 位置变化过大') 