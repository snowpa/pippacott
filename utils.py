import random
from datetime import datetime, timedelta
from app import db
from models import Engineer, Product, Assignment, Parameter
from sqlalchemy import func
import math

# Sample department names
DEPARTMENTS = ["開発部第一課", "開発部第二課", "運用管理課", "サポート第一課", "サポート第二課", "品質管理課"]

# Sample vendor names
VENDORS = ["テクノソリューション", "システム技研", "ネットワークシステムズ", "データコネクト", "クラウドテクノロジー", 
           "セキュリティプロ", "インフォシステム", "ソフトウェア研究所", "ITエンタープライズ", "ミドルウェアシステムズ"]

# Sample product name components
PRODUCT_PREFIXES = ["Cloud", "Secure", "Smart", "Data", "Enterprise", "Hyper", "Ultra", "Power", "Connect", "Rapid"]
PRODUCT_TYPES = ["Manager", "Server", "Controller", "Analyzer", "Gateway", "Monitor", "Suite", "Platform", "Database", "Solution"]

def initialize_default_parameters():
    """Initialize default parameters if they don't exist"""
    default_params = [
        {"key": "min_engineers_per_product", "value": "5", "description": "製品担当エンジニアの最小人数（基準値）"},
        {"key": "max_products_per_engineer", "value": "8", "description": "エンジニアの担当製品数最大数の目安（基準値）"},
        {"key": "target_monthly_overtime", "value": "20", "description": "目標月間残業時間（時間）"},
        {"key": "hours_per_inquiry", "value": "3.5", "description": "問い合わせあたりの対応時間（基準値、時間）"},
        {"key": "inquiry_work_ratio", "value": "0.6", "description": "総稼働に対する問い合わせ対応割合（基準値）"},
        {"key": "total_annual_inquiries", "value": "17000", "description": "年間問い合わせ件数（基準値）"},
        {"key": "annual_working_days", "value": "225", "description": "エンジニアの年間稼働日数（基準値）"},
        {"key": "daily_working_hours", "value": "7.5", "description": "1日の基本労働時間（時間）"}
    ]
    
    for param in default_params:
        if not Parameter.query.filter_by(key=param["key"]).first():
            db.session.add(Parameter(**param))
    
    db.session.commit()

def generate_demo_data():
    """Generate demo data with 40 engineers, 50 products, and realistic assignments"""
    # Create engineers
    for i in range(40):
        department = random.choice(DEPARTMENTS)
        engineer = Engineer(
            name=f"エンジニア {i+1}",
            department=department
        )
        db.session.add(engineer)
    
    db.session.commit()
    
    # Create products with varying inquiry counts (using a power law distribution)
    total_annual_inquiries = int(Parameter.query.filter_by(key="total_annual_inquiries").first().value)
    
    # Generate inquiry counts with 20% negative deviation from baseline
    inquiry_counts = []
    min_engineers = int(Parameter.query.filter_by(key="min_engineers_per_product").first().value)
    
    for i in range(50):
        if i < 10:  # 20% of products with less than baseline
            engineer_diff = random.randint(-3, -1)
        else:  # 80% of products with more than baseline
            engineer_diff = random.randint(0, 3)
            
        # Adjust inquiry count based on engineer difference
        base_inquiry = total_annual_inquiries / 50  # Even distribution as base
        inquiry_count = int(base_inquiry * (1 + engineer_diff * 0.2))  # 20% adjustment per engineer difference
        inquiry_counts.append(max(10, min(inquiry_count, 2000)))  # Cap between 10 and 2000
    
    # Normalize to ensure total matches parameter
    total = sum(inquiry_counts)
    normalized_counts = [int(count * total_annual_inquiries / total) for count in inquiry_counts]
    
    # Make sure the total equals the parameter value (adjust the last product if needed)
    adjustment = total_annual_inquiries - sum(normalized_counts)
    normalized_counts[-1] += adjustment
    
    # Create products
    for i in range(50):
        prefix = random.choice(PRODUCT_PREFIXES)
        type_name = random.choice(PRODUCT_TYPES)
        vendor = random.choice(VENDORS)
        product = Product(
            name=f"{prefix} {type_name} {i+1}",
            vendor=vendor,
            annual_inquiries=normalized_counts[i]
        )
        db.session.add(product)
    
    db.session.commit()
    
    # Create assignments
    engineers = Engineer.query.all()
    products = Product.query.all()
    
    # Sort products by inquiry count (descending)
    products_sorted = sorted(products, key=lambda p: p.annual_inquiries, reverse=True)
    
    # 1. First ensure each product has at least the minimum number of engineers
    min_engineers = int(Parameter.query.filter_by(key="min_engineers_per_product").first().value)
    
    for product in products_sorted:
        # Select random engineers for this product
        available_engineers = random.sample(engineers, min(min_engineers, len(engineers)))
        
        for engineer in available_engineers:
            assignment = Assignment(engineer_id=engineer.id, product_id=product.id)
            db.session.add(assignment)
    
    db.session.commit()
    
    # 2. Then assign additional engineers based on product popularity (more inquiries -> more engineers)
    max_products = int(Parameter.query.filter_by(key="max_products_per_engineer").first().value)
    
    for engineer in engineers:
        # Get current product count for this engineer
        current_product_count = Assignment.query.filter_by(engineer_id=engineer.id).count()
        
        # If engineer has capacity for more products
        if current_product_count < max_products:
            # How many more can they take?
            remaining_capacity = max_products - current_product_count
            
            # Get products this engineer isn't already assigned to
            current_product_ids = [a.product_id for a in Assignment.query.filter_by(engineer_id=engineer.id).all()]
            available_products = [p for p in products_sorted if p.id not in current_product_ids]
            
            # Assign up to remaining capacity, prioritizing products with higher inquiry counts
            for product in available_products[:remaining_capacity]:
                assignment = Assignment(engineer_id=engineer.id, product_id=product.id)
                db.session.add(assignment)
    
    db.session.commit()

def calculate_dashboard_metrics():
    """Calculate metrics for the dashboard - performance optimized version"""
    # Get parameters
    params = {p.key: float(p.value) for p in Parameter.query.all()}
    
    # Get counts directly from database
    engineer_count = db.session.query(func.count(Engineer.id)).scalar() or 0
    product_count = db.session.query(func.count(Product.id)).scalar() or 0
    assignment_count = db.session.query(func.count(Assignment.id)).scalar() or 0

    # Get basic parameter values with defaults
    hours_per_inquiry = params.get('hours_per_inquiry', 2)
    inquiry_work_ratio = params.get('inquiry_work_ratio', 0.6)
    annual_working_days = params.get('annual_working_days', 225)
    daily_working_hours = params.get('daily_working_hours', 7.5)
    max_products_per_engineer = params.get('max_products_per_engineer', 5)
    min_engineers_per_product = params.get('min_engineers_per_product', 2)
    
    # Preload all product inquiry counts and assignments to avoid repeated DB queries
    products = Product.query.all()
    product_inquiry_dict = {p.id: p.annual_inquiries for p in products}
    
    # Get all assignments in one query 
    assignments_by_product = {}
    assignments_by_engineer = {}
    
    all_assignments = Assignment.query.all()
    for a in all_assignments:
        if a.product_id not in assignments_by_product:
            assignments_by_product[a.product_id] = []
        assignments_by_product[a.product_id].append(a)
        
        if a.engineer_id not in assignments_by_engineer:
            assignments_by_engineer[a.engineer_id] = []
        assignments_by_engineer[a.engineer_id].append(a)
    
    # Get product engineer counts in one operation
    product_engineer_counts = {p_id: len(assignments) for p_id, assignments in assignments_by_product.items()}
    
    # Calculate total annual inquiries
    total_annual_inquiries = sum(p.annual_inquiries for p in products)
        
    # Calculate engineer metrics
    engineers = Engineer.query.all()
    engineer_metrics = []
    
    for engineer in engineers:
        # Get assignments for this engineer
        engineer_assignments = assignments_by_engineer.get(engineer.id, [])
        engineer_product_count = len(engineer_assignments)
        
        # Calculate total annual inquiries for this engineer
        total_inquiries = 0
        for assignment in engineer_assignments:
            # Get product inquiry count and divide by number of engineers
            product_id = assignment.product_id
            product_inquiries = product_inquiry_dict.get(product_id, 0)
            engineer_count_for_product = len(assignments_by_product.get(product_id, []))
            if engineer_count_for_product > 0:
                total_inquiries += product_inquiries / engineer_count_for_product
        
        # Calculate work hours
        inquiry_hours = total_inquiries * hours_per_inquiry
        total_working_hours = annual_working_days * daily_working_hours
        total_hours_needed = inquiry_hours / inquiry_work_ratio if inquiry_work_ratio > 0 else 0
        
        # Calculate overtime (monthly)
        overtime_hours = max(0, total_hours_needed - total_working_hours)
        monthly_overtime = overtime_hours / 12
        
        engineer_metrics.append({
            'id': engineer.id,
            'name': engineer.name,
            'department': engineer.department,
            'product_count': engineer_product_count,
            'total_inquiries': round(total_inquiries),
            'monthly_overtime': round(monthly_overtime, 1)
        })
    
    # Sort engineers by overtime (descending)
    engineer_metrics.sort(key=lambda e: e['monthly_overtime'], reverse=True)
    
    # Calculate product metrics
    product_metrics = []
    
    # Precompute the average inquiries per product
    avg_inquiries_per_product = total_annual_inquiries / max(1, len(products))
    
    # Average engineers per product from precomputed values
    avg_engineers_per_product = assignment_count / max(1, product_count)
    
    for product in products:
        # Get engineer count from precomputed dictionary
        product_engineer_count = product_engineer_counts.get(product.id, 0)
        
        # 基準値からの差分を計算
        engineer_diff = product_engineer_count - min_engineers_per_product
        resilience_score = engineer_diff
        
        product_metrics.append({
            'id': product.id,
            'name': product.name,
            'vendor': product.vendor,
            'annual_inquiries': product.annual_inquiries,
            'engineer_count': product_engineer_count,
            'resilience_score': round(resilience_score)
        })
    
    # Sort products by resilience score (ascending)
    product_metrics.sort(key=lambda p: p['resilience_score'])
    
    # Calculate average metrics from precomputed values
    avg_products_per_engineer = assignment_count / max(1, engineer_count)
    
    # Count problematic situations
    overloaded_engineers = sum(1 for e in engineer_metrics if e['product_count'] > max_products_per_engineer)
    understaffed_products = sum(1 for p in product_metrics if p['engineer_count'] < min_engineers_per_product)
    high_overtime_engineers = sum(1 for e in engineer_metrics if e['monthly_overtime'] > 20)  # More than 20 hours overtime
    
    return {
        'summary': {
            'engineer_count': engineer_count,
            'product_count': product_count,
            'total_annual_inquiries': total_annual_inquiries,
            'avg_products_per_engineer': round(avg_products_per_engineer, 1),
            'avg_engineers_per_product': round(avg_engineers_per_product, 1),
            'overloaded_engineers': overloaded_engineers,
            'understaffed_products': understaffed_products,
            'high_overtime_engineers': high_overtime_engineers
        },
        'engineers': engineer_metrics,
        'products': product_metrics
    }

def calculate_simulation_results(data):
    """Calculate simulation results based on input parameters"""
    # Extract parameters from input data
    # Convert string values to appropriate types, providing default values if not present
    total_engineers = int(data.get('total_engineers', 40))
    total_products = int(data.get('total_products', 50))
    hours_per_inquiry = float(data.get('hours_per_inquiry', 2))
    total_annual_inquiries = int(data.get('total_annual_inquiries', 5000))
    inquiry_work_ratio = float(data.get('inquiry_work_ratio', 0.6))
    annual_working_days = int(data.get('annual_working_days', 225))
    daily_working_hours = float(data.get('daily_working_hours', 7.5))
    max_products_per_engineer = int(data.get('max_products_per_engineer', 5))
    min_engineers_per_product = int(data.get('min_engineers_per_product', 2))
    
    # Get target monthly overtime
    target_monthly_overtime = float(Parameter.query.filter_by(key="target_monthly_overtime").first().value)
    annual_overtime_hours = target_monthly_overtime * 12
    
    # Calculate total available work hours per year (including target overtime)
    total_available_hours = total_engineers * (annual_working_days * daily_working_hours + annual_overtime_hours)
    
    # Calculate total hours needed for inquiries
    total_inquiry_hours = total_annual_inquiries * hours_per_inquiry
    
    # Total hours needed (inquiries plus other work)
    total_hours_needed = total_inquiry_hours / inquiry_work_ratio
    
    # Calculate surplus/deficit of hours
    hours_surplus = total_available_hours - total_hours_needed
    
    # Calculate average overtime per engineer per month
    if hours_surplus < 0:
        monthly_overtime_per_engineer = abs(hours_surplus) / (total_engineers * 12) if hours_surplus < 0 else 0
    else:
        monthly_overtime_per_engineer = 0
    
    # Calculate average products per engineer
    # First, ensure every product has minimum engineers
    min_assignments = total_products * min_engineers_per_product
    
    # Then distribute remaining capacity
    remaining_capacity = (total_engineers * max_products_per_engineer) - min_assignments
    
    # If remaining capacity is negative, we can't meet minimum staffing
    if remaining_capacity < 0:
        # Calculate the number of products that would be understaffed
        understaffed_products = math.ceil(abs(remaining_capacity) / min_engineers_per_product)
        # We can still calculate average products per engineer
        # Adjust calculation to ensure it's based on actual capacity
        total_possible_assignments = total_engineers * max_products_per_engineer
        avg_products_per_engineer = min(max_products_per_engineer, (total_possible_assignments / total_engineers))
    else:
        understaffed_products = 0
        # We'll distribute the remaining capacity optimally
        # Estimate that products get assigned in proportion to their inquiry volume
        # which follows a power law distribution
        # Cap at 3 extra engineers per product on average
        additional_assignments = min(remaining_capacity, total_products * 3)
        total_assignments = min_assignments + additional_assignments
        # Calculate actual average products per engineer
        avg_products_per_engineer = min(max_products_per_engineer, total_assignments / total_engineers)
    
    # Calculate average engineers per product
    avg_engineers_per_product = (total_engineers * avg_products_per_engineer) / total_products
    
    # Calculate coverage ratio (actual vs. desired minimum)
    coverage_ratio = avg_engineers_per_product / min_engineers_per_product
    
    # Calculate average inquiries per engineer
    avg_inquiries_per_engineer = total_annual_inquiries / total_engineers
    
    # Calculate optimal engineer count based on target monthly overtime
    target_monthly_overtime = float(Parameter.query.filter_by(key="target_monthly_overtime").first().value)
    annual_overtime_hours = target_monthly_overtime * 12
    optimal_engineer_count = math.ceil(
        total_hours_needed / 
        ((annual_working_days * daily_working_hours) + annual_overtime_hours)
    )
    
    # Calculate optimal product count based on engineer capacity
    # This is the maximum number of products that can be fully staffed
    # Each product needs min_engineers_per_product engineers
    # Each engineer can handle max_products_per_engineer products
    optimal_product_count = math.floor((total_engineers * max_products_per_engineer) / min_engineers_per_product)
    
    return {
        'monthly_overtime_per_engineer': round(monthly_overtime_per_engineer, 1),
        'avg_products_per_engineer': round(avg_products_per_engineer, 1),
        'avg_engineers_per_product': round(avg_engineers_per_product, 1),
        'coverage_ratio': round(coverage_ratio, 2),
        'avg_inquiries_per_engineer': round(avg_inquiries_per_engineer),
        'understaffed_products': understaffed_products,
        'optimal_engineer_count': optimal_engineer_count,
        'engineer_surplus_deficit': optimal_engineer_count - total_engineers,
        'optimal_product_count': optimal_product_count,
        'product_surplus_deficit': optimal_product_count - total_products,
        'hours_surplus_deficit': round(hours_surplus)
    }
