import os
import random
import string
from app import app, db
from models import Department, Engineer, Product, Settings, engineer_product, Simulation
from datetime import datetime

def create_demo_data():
    """デモデータを作成する関数"""
    print("デモデータの作成を開始します...")
    
    # すでにデータがある場合はスキップ
    if Department.query.count() > 0:
        print("データベースにはすでにデータが存在します。シードをスキップします。")
        return

    try:
        # 部署の作成
        departments = [
            "第一技術部", "第二技術部", "第三技術部", "第四技術部", 
            "インフラ技術部", "ネットワーク技術部", "クラウド技術部", "セキュリティ技術部"
        ]
        
        department_objects = []
        for dept_name in departments:
            dept = Department(name=dept_name)
            db.session.add(dept)
            department_objects.append(dept)
        
        db.session.commit()
        print(f"{len(departments)}個の部署を作成しました")

        # 設定の作成（既存の場合は作成しない）
        if Settings.query.count() == 0:
            settings = Settings(
                min_engineers_per_product=2,
                max_products_per_engineer=5,
                hours_per_inquiry=1.0,
                inquiry_work_ratio=0.6,
                work_hours_per_day=7.5,
                work_days_per_year=240
            )
            db.session.add(settings)
            db.session.commit()
            print("設定を作成しました")

        # エンジニアの作成（40名）
        engineer_first_names = [
            "太郎", "次郎", "三郎", "四郎", "五郎", "六郎", "七郎", "八郎",
            "一郎", "正", "誠", "健", "裕", "秀", "浩", "清", "和", "明", "聡", "修"
        ]
        
        engineer_last_names = [
            "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
            "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上",
            "木村", "林", "斎藤", "清水", "山崎", "森", "池田", "橋本", "阿部"
        ]
        
        engineers = []
        for i in range(40):
            first_name = random.choice(engineer_first_names)
            last_name = random.choice(engineer_last_names)
            full_name = f"{last_name} {first_name}"
            department = random.choice(department_objects)
            
            engineer = Engineer(name=full_name, department=department)
            db.session.add(engineer)
            engineers.append(engineer)
        
        db.session.commit()
        print("40名のエンジニアを作成しました")

        # 製品の作成（60個）
        vendor_names = [
            "マイクロソフト", "アップル", "グーグル", "アマゾン", "オラクル", "シスコ", "デル", "HPE",
            "IBM", "インテル", "AMD", "エプソン", "キヤノン", "富士通", "NEC", "日立", "東芝", "パナソニック",
            "ソニー", "サムスン"
        ]
        
        products = []
        for i in range(60):
            vendor = random.choice(vendor_names)
            product_number = ''.join(random.choices(string.ascii_uppercase, k=2)) + '-' + ''.join(random.choices(string.digits, k=4))
            
            # 製品名を生成（製品タイプ + 製品コード）
            product_types = ["サーバー", "ストレージ", "ネットワーク機器", "セキュリティ機器", "クラウドサービス", 
                            "仮想化", "OS", "データベース", "アプリケーション", "デバイス"]
            product_type = random.choice(product_types)
            product_name = f"{vendor} {product_type} {product_number}"
            
            # 年間問い合わせ数を設定（0～500の範囲で、一部の製品は特に多い）
            if random.random() < 0.2:  # 20%の製品は問い合わせが多い
                annual_inquiries = random.randint(300, 2000)
            else:
                annual_inquiries = random.randint(10, 300)
            
            product = Product(name=product_name, vendor=vendor, annual_inquiries=annual_inquiries)
            db.session.add(product)
            products.append(product)
        
        db.session.commit()
        print("60個の製品を作成しました")

        # エンジニアと製品の割り当て
        for engineer in engineers:
            # 各エンジニアに1～5個の製品をランダムに割り当て
            num_products = random.randint(1, 5)
            assigned_products = random.sample(products, num_products)
            
            for product in assigned_products:
                engineer.products.append(product)
        
        db.session.commit()
        print("エンジニアと製品の割り当てを完了しました")

        # 各製品について、担当エンジニアが少なすぎる場合は追加で割り当て
        settings = Settings.query.first()
        min_engineers = settings.min_engineers_per_product
        
        for product in products:
            current_count = product.engineers.count()
            
            if current_count < min_engineers:
                needed = min_engineers - current_count
                # この製品をまだ担当していないエンジニアを取得
                available_engineers = [e for e in engineers if product not in e.products]
                
                if available_engineers:
                    # 必要な数だけランダムに選んで割り当て
                    assigned_engineers = random.sample(available_engineers, min(needed, len(available_engineers)))
                    for engineer in assigned_engineers:
                        engineer.products.append(product)
        
        db.session.commit()
        print("製品の担当エンジニア数を調整しました")
        
        print("デモデータの作成が完了しました！")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    with app.app_context():
        create_demo_data()