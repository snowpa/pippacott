from app import db
from models import Engineer, Product, Settings, Simulation
import math

def calculate_workload(annual_inquiries, settings):
    """年間問い合わせ数から必要な年間稼働時間を計算"""
    return annual_inquiries * settings.hours_per_inquiry

def calculate_staffing(annual_inquiries, settings):
    """年間問い合わせ数から必要なエンジニア数を計算"""
    # 年間の一人あたり稼働時間
    annual_work_hours = settings.work_hours_per_day * settings.work_days_per_year
    
    # 問い合わせ対応に充てる時間の割合を考慮
    available_hours_for_inquiries = annual_work_hours * settings.inquiry_work_ratio
    
    # 必要なエンジニア数を計算
    workload = calculate_workload(annual_inquiries, settings)
    required_engineers = workload / available_hours_for_inquiries if available_hours_for_inquiries > 0 else 0
    
    # 切り上げて整数に
    return math.ceil(required_engineers)

def run_simulation(simulation_id):
    """シミュレーションを実行して結果を返す"""
    simulation = Simulation.query.get(simulation_id)
    if not simulation:
        return {'success': False, 'message': 'シミュレーションが見つかりませんでした'}
    
    settings = Settings.query.first()
    if not settings:
        return {'success': False, 'message': '設定が見つかりませんでした'}
    
    # シミュレーション用のパラメータ計算
    sim_settings = {
        'min_engineers_per_product': settings.min_engineers_per_product,
        'max_products_per_engineer': math.ceil(settings.max_products_per_engineer * (1 + simulation.max_products_per_engineer_change / 100)),
        'hours_per_inquiry': settings.hours_per_inquiry * (1 + simulation.hours_per_inquiry_change / 100),
        'inquiry_work_ratio': min(1.0, settings.inquiry_work_ratio * (1 + simulation.inquiry_work_ratio_change / 100)),
        'work_hours_per_day': settings.work_hours_per_day,
        'work_days_per_year': settings.work_days_per_year
    }
    
    # 現在のエンジニア数と製品数の取得
    current_engineers_count = Engineer.query.count()
    current_products_count = Product.query.count()
    
    # シミュレーションでのエンジニア数と製品数
    sim_engineers_count = math.ceil(current_engineers_count * (1 + simulation.total_engineers_change / 100))
    sim_products_count = math.ceil(current_products_count * (1 + simulation.total_products_change / 100))
    
    # 製品ごとの充足率とエンジニア数を計算
    current_products_data = []
    sim_products_data = []
    
    for product in Product.query.all():
        # 現在の状態
        current_engineer_count = product.engineers.count()
        current_required_engineers = calculate_staffing(product.annual_inquiries, settings)
        if current_required_engineers > 0:
            current_sufficiency_rate = min(100, (current_engineer_count / current_required_engineers) * 100)
        else:
            current_sufficiency_rate = 100
        
        current_products_data.append({
            'id': product.id,
            'name': product.name,
            'engineer_count': current_engineer_count,
            'required_engineers': current_required_engineers,
            'sufficiency_rate': round(current_sufficiency_rate, 2),
            'annual_inquiries': product.annual_inquiries
        })
        
        # シミュレーション後の状態
        # 比例配分でエンジニア数を調整
        sim_engineer_count = round(current_engineer_count * (sim_engineers_count / current_engineers_count)) if current_engineers_count > 0 else 0
        
        # 問い合わせ数を調整 (年間問い合わせ件数の変化率を適用)
        sim_annual_inquiries = round(product.annual_inquiries * (1 + simulation.annual_inquiries_change / 100))
        
        # シミュレーション設定を使って必要エンジニア数を計算
        sim_required_engineers = calculate_staffing(sim_annual_inquiries, type('Settings', (), sim_settings))
        if sim_required_engineers > 0:
            sim_sufficiency_rate = min(100, (sim_engineer_count / sim_required_engineers) * 100)
        else:
            sim_sufficiency_rate = 100
        
        sim_products_data.append({
            'id': product.id,
            'name': product.name,
            'engineer_count': sim_engineer_count,
            'required_engineers': sim_required_engineers,
            'sufficiency_rate': round(sim_sufficiency_rate, 2),
            'annual_inquiries': sim_annual_inquiries
        })
    
    # エンジニアごとの残業時間予測
    current_engineers_data = []
    sim_engineers_data = []
    
    for engineer in Engineer.query.all():
        # 現在の状態
        current_total_workload = 0
        for product in engineer.products:
            assigned_engineers = product.engineers.count() or 1
            product_workload = calculate_workload(product.annual_inquiries, settings) / assigned_engineers
            current_total_workload += product_workload
        
        current_annual_work_hours = settings.work_hours_per_day * settings.work_days_per_year
        
        if current_total_workload > current_annual_work_hours:
            current_overtime_hours = current_total_workload - current_annual_work_hours
        else:
            current_overtime_hours = 0
        
        current_daily_overtime = current_overtime_hours / settings.work_days_per_year
        
        current_engineers_data.append({
            'id': engineer.id,
            'name': engineer.name,
            'product_count': len(engineer.products),
            'total_workload': round(current_total_workload, 2),
            'annual_work_hours': current_annual_work_hours,
            'overtime_hours': round(current_overtime_hours, 2),
            'daily_overtime': round(current_daily_overtime, 2),
            'workload_percent': round((current_total_workload / current_annual_work_hours) * 100, 2)
        })
        
        # シミュレーション後の状態
        # 担当製品数の最大値を調整
        max_products = min(len(engineer.products), sim_settings['max_products_per_engineer'])
        
        # シミュレーション設定を使って稼働時間を計算
        sim_total_workload = 0
        for i, product in enumerate(engineer.products):
            if i >= max_products:
                break
            
            # シミュレーション後の担当エンジニア数を推定
            sim_assigned_engineers = round(product.engineers.count() * (sim_engineers_count / current_engineers_count)) if current_engineers_count > 0 else 1
            sim_assigned_engineers = max(1, sim_assigned_engineers)  # 最低1人
            
            # シミュレーション後の問い合わせ数を推定
            sim_annual_inquiries = round(product.annual_inquiries * (1 + simulation.annual_inquiries_change / 100))
            
            sim_product_workload = calculate_workload(sim_annual_inquiries, type('Settings', (), sim_settings)) / sim_assigned_engineers
            sim_total_workload += sim_product_workload
        
        sim_annual_work_hours = sim_settings['work_hours_per_day'] * sim_settings['work_days_per_year']
        
        if sim_total_workload > sim_annual_work_hours:
            sim_overtime_hours = sim_total_workload - sim_annual_work_hours
        else:
            sim_overtime_hours = 0
        
        sim_daily_overtime = sim_overtime_hours / sim_settings['work_days_per_year']
        
        sim_engineers_data.append({
            'id': engineer.id,
            'name': engineer.name,
            'product_count': min(len(engineer.products), max_products),
            'total_workload': round(sim_total_workload, 2),
            'annual_work_hours': sim_annual_work_hours,
            'overtime_hours': round(sim_overtime_hours, 2),
            'daily_overtime': round(sim_daily_overtime, 2),
            'workload_percent': round((sim_total_workload / sim_annual_work_hours) * 100, 2)
        })
    
    # 全体の充足率
    current_total_required = sum(p['required_engineers'] for p in current_products_data)
    current_total_engineers = current_engineers_count
    current_overall_sufficiency = min(100, (current_total_engineers / current_total_required) * 100) if current_total_required > 0 else 100
    
    sim_total_required = sum(p['required_engineers'] for p in sim_products_data)
    sim_total_engineers = sim_engineers_count
    sim_overall_sufficiency = min(100, (sim_total_engineers / sim_total_required) * 100) if sim_total_required > 0 else 100
    
    # 平均残業時間
    current_avg_overtime = sum(e['daily_overtime'] for e in current_engineers_data) / len(current_engineers_data) if current_engineers_data else 0
    sim_avg_overtime = sum(e['daily_overtime'] for e in sim_engineers_data) / len(sim_engineers_data) if sim_engineers_data else 0
    
    return {
        'success': True,
        'simulation_info': {
            'id': simulation.id,
            'name': simulation.name,
            'parameters': {
                'total_engineers_change': simulation.total_engineers_change,
                'total_products_change': simulation.total_products_change,
                'hours_per_inquiry_change': simulation.hours_per_inquiry_change,
                'max_products_per_engineer_change': simulation.max_products_per_engineer_change,
                'inquiry_work_ratio_change': simulation.inquiry_work_ratio_change
            }
        },
        'current': {
            'total_engineers': current_engineers_count,
            'total_products': current_products_count,
            'overall_sufficiency': round(current_overall_sufficiency, 2),
            'avg_overtime': round(current_avg_overtime, 2),
            'products': current_products_data,
            'engineers': current_engineers_data
        },
        'simulation_result': {
            'total_engineers': sim_engineers_count,
            'total_products': sim_products_count,
            'overall_sufficiency': round(sim_overall_sufficiency, 2),
            'avg_overtime': round(sim_avg_overtime, 2),
            'products': sim_products_data,
            'engineers': sim_engineers_data
        }
    }
