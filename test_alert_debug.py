#!/usr/bin/env python3
"""Debug script to test critical alert processing"""

import sys
import os
sys.path.append('/Users/bg/work/codes/springboot/ljwx/flt/ljwx-bigscreen/bigscreen')

from bigScreen import create_app
from bigScreen.models import AlertRules, db
from bigScreen.device import get_device_user_org_info

app = create_app()

with app.app_context():
    print("=== Testing Critical Alert Processing ===")
    
    # Test 1: Check alert rule lookup
    event_type = "one_key_alarm"
    print(f"\n1. Testing alert rule lookup for: {event_type}")
    rule = AlertRules.query.filter_by(rule_type=event_type, is_deleted=False).first()
    if rule:
        print(f"   ✅ Found rule: {rule.rule_type}, severity: {rule.severity_level}")
        print(f"   Alert message: {rule.alert_message}")
    else:
        print(f"   ❌ No rule found for {event_type}")
        # List all available rules
        all_rules = AlertRules.query.filter_by(is_deleted=False).all()
        print(f"   Available rules:")
        for r in all_rules:
            print(f"     - {r.rule_type} (severity: {r.severity_level})")
    
    # Test 2: Check device user org lookup
    device_sn = "CRFTQ23409001890"
    print(f"\n2. Testing device user org lookup for: {device_sn}")
    device_user_org = get_device_user_org_info(device_sn)
    print(f"   Result: {device_user_org}")
    
    if device_user_org.get('success'):
        print(f"   ✅ Device lookup successful")
        print(f"   User: {device_user_org.get('user_name')}")
        print(f"   Org: {device_user_org.get('org_name')}")
    else:
        print(f"   ❌ Device lookup failed: {device_user_org.get('message')}")
    
    # Test 3: Check if critical alert would trigger SocketIO
    if rule and device_user_org.get('success'):
        print(f"\n3. Testing critical alert conditions")
        if rule.severity_level == 'critical':
            print(f"   ✅ Rule has critical severity - SocketIO emission would trigger")
            print(f"   Alert data would include:")
            print(f"     - device_sn: {device_sn}")
            print(f"     - user_name: {device_user_org.get('user_name')}")
            print(f"     - org_name: {device_user_org.get('org_name')}")
            print(f"     - severity_level: {rule.severity_level}")
        else:
            print(f"   ❌ Rule severity is '{rule.severity_level}', not 'critical'")
    else:
        print(f"\n3. ❌ Cannot test critical alert - missing rule or device info")
    
    print(f"\n=== Debug Complete ===")