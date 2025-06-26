-- 灵境万象系统客户端数据库初始化 v1.2.16 - 管理员分离功能
-- 执行时间: $(date '+%Y-%m-%d %H:%M:%S')

-- 1. 确保sys_role表包含is_admin字段
ALTER TABLE sys_role ADD COLUMN IF NOT EXISTS is_admin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为管理员角色（0普通角色，1管理员角色）' AFTER status;

-- 2. 初始化管理员角色标记
UPDATE sys_role SET is_admin = 1 WHERE role_code IN ('ADMIN', 'DAdmin');
UPDATE sys_role SET is_admin = 0 WHERE role_code NOT IN ('ADMIN', 'DAdmin');

-- 3. 创建员工角色（如果不存在）
INSERT IGNORE INTO sys_role (role_name, role_code, sort, status, is_admin, remark, create_time) VALUES
('员工', 'EMPLOYEE', 99, 1, 0, '普通员工角色', NOW());

-- 4. 插入默认测试数据（演示用）
INSERT IGNORE INTO sys_user (id, user_name, nick_name, real_name, email, phone, user_card_number, device_sn, working_years, position, password, status, create_time) VALUES
(1001, 'employee01', '员工01', '张三', 'zhangsan@company.com', '18911111111', '1-001', 'WATCH001', 1, '技术员', '$2a$10$N.zmdr9k7uOCQb8gKhKHcOxHjMHQo0JO0T2a5i6GXM8k8JRR8I8XG', 1, NOW()),
(1002, 'employee02', '员工02', '李四', 'lisi@company.com', '18922222222', '1-002', 'WATCH002', 2, '质检员', '$2a$10$N.zmdr9k7uOCQb8gKhKHcOxHjMHQo0JO0T2a5i6GXM8k8JRR8I8XG', 1, NOW());

-- 5. 分配员工角色
INSERT IGNORE INTO sys_user_role (user_id, role_id) VALUES
(1001, (SELECT id FROM sys_role WHERE role_code = 'EMPLOYEE' LIMIT 1)),
(1002, (SELECT id FROM sys_role WHERE role_code = 'EMPLOYEE' LIMIT 1));

-- 6. 验证数据
SELECT '✅ 管理员分离功能初始化完成' AS status;
SELECT CONCAT('📊 角色统计: 管理员角色 ', COUNT(*), ' 个') AS admin_roles FROM sys_role WHERE is_admin = 1;
SELECT CONCAT('👥 员工角色 ', COUNT(*), ' 个') AS employee_roles FROM sys_role WHERE is_admin = 0; 