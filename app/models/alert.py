from .base import db
class AlertInfo(db.Model):
    __tablename__ = 'alert_info'
    id = db.Column(db.Integer, primary_key=True) # 主键
    deviceSn = db.Column(db.String(64)) # 设备序列号
    customerId = db.Column(db.String(32)) # 客户ID
    userId = db.Column(db.String(32)) # 用户ID
    orgId = db.Column(db.String(32)) # 组织ID
    alertType = db.Column(db.String(32)) # 告警类型
    severityLevel = db.Column(db.String(16)) # 严重级别
    message = db.Column(db.String(256)) # 告警信息
    status = db.Column(db.String(16)) # 状态
    resolved_at = db.Column(db.DateTime) # 解决时间
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DeviceMessage(db.Model):
    __tablename__ = 'device_message'
    id = db.Column(db.Integer, primary_key=True) # 主键
    deviceSn = db.Column(db.String(64)) # 设备序列号
    customerId = db.Column(db.String(32)) # 客户ID
    userId = db.Column(db.String(32)) # 用户ID
    orgId = db.Column(db.String(32)) # 组织ID
    message = db.Column(db.String(256)) # 消息内容
    message_type = db.Column(db.String(32)) # 消息类型
    sender_type = db.Column(db.String(16)) # 发送方类型
    receiver_type = db.Column(db.String(16)) # 接收方类型
    message_status = db.Column(db.String(16)) # 消息状态
    department_info = db.Column(db.String(64)) # 部门信息
    sent_time = db.Column(db.DateTime) # 发送时间
    read_time = db.Column(db.DateTime) # 阅读时间
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 