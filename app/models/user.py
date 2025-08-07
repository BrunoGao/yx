from .base import db
class UserInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True) # 主键
    userId = db.Column(db.String(32)) # 用户ID
    orgId = db.Column(db.String(32)) # 组织ID
    deviceSn = db.Column(db.String(64)) # 设备序列号
    phone = db.Column(db.String(32)) # 手机号
    userName = db.Column(db.String(64)) # 用户名
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 