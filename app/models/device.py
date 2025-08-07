from .base import db
class DeviceInfo(db.Model):
    __tablename__ = 'device_info'
    id = db.Column(db.Integer, primary_key=True) # 主键
    deviceSn = db.Column(db.String(64)) # 设备序列号
    deviceName = db.Column(db.String(64)) # 设备名称
    customerId = db.Column(db.String(32)) # 客户ID
    status = db.Column(db.String(16)) # 状态
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 