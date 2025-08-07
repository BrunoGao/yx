from .base import db
class OrgInfo(db.Model):
    __tablename__ = 'org_info'
    id = db.Column(db.Integer, primary_key=True) # 主键
    orgId = db.Column(db.String(32)) # 组织ID
    orgName = db.Column(db.String(64)) # 组织名称
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 