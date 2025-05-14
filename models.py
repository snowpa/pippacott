from app import db
from datetime import datetime

# 担当割り当てのための中間テーブル
engineer_product = db.Table('engineer_product',
    db.Column('engineer_id', db.Integer, db.ForeignKey('engineer.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    engineers = db.relationship('Engineer', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'

class Engineer(db.Model):
    __tablename__ = 'engineer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 多対多のリレーションシップ
    products = db.relationship('Product', secondary=engineer_product,
                              backref=db.backref('engineers', lazy='dynamic'))

    def __repr__(self):
        return f'<Engineer {self.name}>'

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    annual_inquiries = db.Column(db.Integer, default=0)  # 年間問い合わせ数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    min_engineers_per_product = db.Column(db.Integer, default=2)  # 製品担当エンジニアの最小人数
    max_products_per_engineer = db.Column(db.Integer, default=5)  # エンジニアの担当製品数最大数
    hours_per_inquiry = db.Column(db.Float, default=1.0)  # 問い合わせあたりの対応時間(時間)
    inquiry_work_ratio = db.Column(db.Float, default=0.6)  # 総稼働に対する問い合わせ対応割合
    work_hours_per_day = db.Column(db.Float, default=7.5)  # 1日あたりの稼働時間
    work_days_per_year = db.Column(db.Integer, default=240)  # 年間稼働日数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Settings {self.id}>'

class Simulation(db.Model):
    __tablename__ = 'simulation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_engineers_change = db.Column(db.Float, default=0.0)  # 総エンジニア数の変化率
    total_products_change = db.Column(db.Float, default=0.0)  # 総製品数の変化率
    annual_inquiries_change = db.Column(db.Float, default=0.0)  # 年間問い合わせ件数の変化率
    hours_per_inquiry_change = db.Column(db.Float, default=0.0)  # 問い合わせあたりの対応時間の変化率
    max_products_per_engineer_change = db.Column(db.Float, default=0.0)  # エンジニアあたり製品数上限の変化率
    inquiry_work_ratio_change = db.Column(db.Float, default=0.0)  # 総稼働に対する問い合わせ対応割合の変化率
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Simulation {self.name}>'
