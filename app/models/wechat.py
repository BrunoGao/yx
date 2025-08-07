from .base import db
class WechatConfig(db.Model):
    __tablename__ = 'wechat_config'
    id = db.Column(db.Integer, primary_key=True) # 主键
    app_id = db.Column(db.String(64)) # 微信AppID
    app_secret = db.Column(db.String(128)) # 微信密钥
    template_id = db.Column(db.String(64)) # 模板ID
    user_openid = db.Column(db.String(64)) # 用户openid
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 