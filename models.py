from app import db
from datetime import datetime

# Engineer model
class Engineer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 氏名
    department = db.Column(db.String(100), nullable=False)  # 所属課名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One engineer can be assigned to many products
    assignments = db.relationship('Assignment', back_populates='engineer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Engineer {self.name}>'

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 製品名
    vendor = db.Column(db.String(100), nullable=False)  # ベンダー名
    annual_inquiries = db.Column(db.Integer, default=0)  # 年間問い合わせ数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One product can be assigned to many engineers
    assignments = db.relationship('Assignment', back_populates='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'

# Assignment model (Many-to-Many relationship between Engineer and Product)
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    engineer_id = db.Column(db.Integer, db.ForeignKey('engineer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    engineer = db.relationship('Engineer', back_populates='assignments')
    product = db.relationship('Product', back_populates='assignments')
    
    def __repr__(self):
        return f'<Assignment Engineer={self.engineer_id} Product={self.product_id}>'

# Parameter model for system settings
class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Parameter {self.key}={self.value}>'
