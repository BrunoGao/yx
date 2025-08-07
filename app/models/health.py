from .base import db
class UserHealthData(db.Model):
    __tablename__ = 'user_health_data_new'
    id = db.Column(db.Integer, primary_key=True) # 主键
    deviceSn = db.Column(db.String(64)) # 设备序列号
    userId = db.Column(db.String(32)) # 用户ID
    orgId = db.Column(db.String(32)) # 组织ID
    heartRate = db.Column(db.Float) # 心率
    systolicPressure = db.Column(db.Float) # 收缩压
    diastolicPressure = db.Column(db.Float) # 舒张压
    bloodOxygen = db.Column(db.Float) # 血氧
    bodyTemperature = db.Column(db.Float) # 体温
    latitude = db.Column(db.Float) # 纬度
    longitude = db.Column(db.Float) # 经度
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 