
from app import db
from datetime import datetime
from sqlalchemy import Index

class Engineer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    max_products = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignments = db.relationship('Assignment', back_populates='engineer', lazy='joined')
    
    __table_args__ = (
        Index('idx_engineer_department', 'department'),
    )

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    annual_inquiries = db.Column(db.Integer, default=0)
    min_engineers = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignments = db.relationship('Assignment', back_populates='product', lazy='joined')
    
    __table_args__ = (
        Index('idx_product_vendor', 'vendor'),
        Index('idx_product_inquiries', 'annual_inquiries'),
    )

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    engineer_id = db.Column(db.Integer, db.ForeignKey('engineer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    engineer = db.relationship('Engineer', back_populates='assignments')
    product = db.relationship('Product', back_populates='assignments')
    
    __table_args__ = (
        Index('idx_assignment_engineer', 'engineer_id'),
        Index('idx_assignment_product', 'product_id'),
    )
