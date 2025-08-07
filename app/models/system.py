from .base import db
class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    id = db.Column(db.Integer, primary_key=True) # 主键
    key = db.Column(db.String(64)) # 配置键
    value = db.Column(db.String(256)) # 配置值
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DepartmentInfo(db.Model):
    __tablename__ = 'department_info'
    id = db.Column(db.Integer, primary_key=True) # 主键
    orgId = db.Column(db.String(32)) # 组织ID
    departmentId = db.Column(db.String(32)) # 部门ID
    departmentName = db.Column(db.String(64)) # 部门名称
    created_at = db.Column(db.DateTime) # 创建时间
    updated_at = db.Column(db.DateTime) # 更新时间
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 