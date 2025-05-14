from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Engineer, Product, Department, Settings, Simulation, engineer_product
from forms import EngineerForm, ProductForm, DepartmentForm, SettingsForm, SimulationForm
from utils import calculate_workload, calculate_staffing, run_simulation
import json

# ダッシュボード
@app.route('/')
def dashboard():
    settings = Settings.query.first()
    if not settings:
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
    
    total_engineers = Engineer.query.count()
    total_products = Product.query.count()
    
    # 担当エンジニアが不足している製品を特定
    understaffed_products = []
    for product in Product.query.all():
        engineer_count = product.engineers.count()
        if engineer_count < settings.min_engineers_per_product:
            understaffed_products.append({
                'id': product.id,
                'name': product.name,
                'engineer_count': engineer_count,
                'minimum_required': settings.min_engineers_per_product
            })
    
    # 担当製品が多すぎるエンジニアを特定
    overloaded_engineers = []
    for engineer in Engineer.query.all():
        product_count = len(engineer.products)
        if product_count > settings.max_products_per_engineer:
            overloaded_engineers.append({
                'id': engineer.id,
                'name': engineer.name,
                'product_count': product_count,
                'maximum_allowed': settings.max_products_per_engineer
            })
    
    # 製品ごとの充足率を計算
    products_data = []
    for product in Product.query.all():
        engineer_count = product.engineers.count()
        required_engineers = calculate_staffing(product.annual_inquiries, settings)
        if required_engineers > 0:
            sufficiency_rate = min(100, round((engineer_count / required_engineers) * 100))
        else:
            sufficiency_rate = 100
        
        products_data.append({
            'id': product.id,
            'name': product.name,
            'engineer_count': engineer_count,
            'required_engineers': required_engineers,
            'sufficiency_rate': sufficiency_rate,
            'annual_inquiries': product.annual_inquiries
        })
    
    # エンジニアごとの予測残業時間を計算
    engineers_data = []
    for engineer in Engineer.query.all():
        total_workload = 0
        for product in engineer.products:
            # 製品の担当者数で均等に分担すると仮定
            assigned_engineers = product.engineers.count() or 1
            product_workload = calculate_workload(product.annual_inquiries, settings) / assigned_engineers
            total_workload += product_workload
        
        # 年間の総稼働時間
        annual_work_hours = settings.work_hours_per_day * settings.work_days_per_year
        
        # 残業時間を計算（負の値の場合は0に）
        if total_workload > annual_work_hours:
            overtime_hours = total_workload - annual_work_hours
        else:
            overtime_hours = 0
            
        # 1日あたりの平均残業時間
        daily_overtime = round(overtime_hours / settings.work_days_per_year, 2)
        
        engineers_data.append({
            'id': engineer.id,
            'name': engineer.name,
            'product_count': len(engineer.products),
            'total_workload': round(total_workload, 2),
            'annual_work_hours': annual_work_hours,
            'overtime_hours': round(overtime_hours, 2),
            'daily_overtime': daily_overtime,
            'workload_percent': round((total_workload / annual_work_hours) * 100, 2)
        })
    
    # 製品データと必要エンジニア数から全体の充足率を計算
    total_required_engineers = sum(product['required_engineers'] for product in products_data)
    overall_sufficiency = min(100, (total_engineers / total_required_engineers) * 100) if total_required_engineers > 0 else 100
    
    return render_template('dashboard.html', 
                          total_engineers=total_engineers,
                          total_products=total_products,
                          understaffed_products=understaffed_products,
                          overloaded_engineers=overloaded_engineers,
                          products_data=products_data,
                          engineers_data=engineers_data,
                          settings=settings,
                          overall_sufficiency=round(overall_sufficiency, 1))

# エンジニア管理
@app.route('/engineers')
def engineers():
    engineers = Engineer.query.all()
    departments = Department.query.all()
    form = EngineerForm()
    form.department_id.choices = [(d.id, d.name) for d in departments]
    return render_template('engineers.html', engineers=engineers, form=form, departments=departments)

@app.route('/engineers/add', methods=['POST'])
def add_engineer():
    form = EngineerForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        engineer = Engineer(
            name=form.name.data,
            department_id=form.department_id.data
        )
        db.session.add(engineer)
        db.session.commit()
        flash('エンジニアが正常に追加されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('engineers'))

@app.route('/engineers/edit/<int:id>', methods=['POST'])
def edit_engineer(id):
    engineer = Engineer.query.get_or_404(id)
    form = EngineerForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        engineer.name = form.name.data
        engineer.department_id = form.department_id.data
        db.session.commit()
        flash('エンジニア情報が正常に更新されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('engineers'))

@app.route('/engineers/delete/<int:id>', methods=['POST'])
def delete_engineer(id):
    engineer = Engineer.query.get_or_404(id)
    db.session.delete(engineer)
    db.session.commit()
    flash('エンジニアが正常に削除されました！', 'success')
    return redirect(url_for('engineers'))

# 製品管理
@app.route('/products')
def products():
    products = Product.query.all()
    form = ProductForm()
    return render_template('products.html', products=products, form=form)

@app.route('/products/add', methods=['POST'])
def add_product():
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            vendor=form.vendor.data,
            annual_inquiries=form.annual_inquiries.data
        )
        db.session.add(product)
        db.session.commit()
        flash('製品が正常に追加されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('products'))

@app.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm()
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.vendor = form.vendor.data
        product.annual_inquiries = form.annual_inquiries.data
        db.session.commit()
        flash('製品情報が正常に更新されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('products'))

@app.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('製品が正常に削除されました！', 'success')
    return redirect(url_for('products'))

# 部署管理
@app.route('/departments')
def departments():
    departments = Department.query.all()
    form = DepartmentForm()
    return render_template('settings.html', departments=departments, form=form, active_tab='departments')

@app.route('/departments/add', methods=['POST'])
def add_department():
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(
            name=form.name.data
        )
        db.session.add(department)
        db.session.commit()
        flash('部署が正常に追加されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('departments'))

@app.route('/departments/edit/<int:id>', methods=['POST'])
def edit_department(id):
    department = Department.query.get_or_404(id)
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department.name = form.name.data
        db.session.commit()
        flash('部署情報が正常に更新されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('departments'))

@app.route('/departments/delete/<int:id>', methods=['POST'])
def delete_department(id):
    department = Department.query.get_or_404(id)
    # 部署に関連するエンジニアがいないか確認
    if Engineer.query.filter_by(department_id=id).first():
        flash('この部署に属するエンジニアが存在するため削除できません。', 'danger')
    else:
        db.session.delete(department)
        db.session.commit()
        flash('部署が正常に削除されました！', 'success')
    return redirect(url_for('departments'))

# 担当割り当て
@app.route('/assignments')
def assignments():
    engineers = Engineer.query.all()
    products = Product.query.all()
    
    # エンジニアと製品の担当関係のデータを準備
    assignments_data = []
    for engineer in engineers:
        product_ids = [p.id for p in engineer.products]
        assignments_data.append({
            'id': engineer.id,
            'name': engineer.name,
            'department': engineer.department.name,
            'product_ids': product_ids,
            'product_count': len(product_ids)
        })
    
    return render_template('assignments.html', 
                          engineers=engineers, 
                          products=products, 
                          assignments_data=json.dumps(assignments_data))

@app.route('/assignments/update', methods=['POST'])
def update_assignments():
    data = request.json
    
    try:
        for engineer_data in data:
            engineer_id = engineer_data['engineerId']
            product_ids = engineer_data['productIds']
            
            engineer = Engineer.query.get_or_404(engineer_id)
            engineer.products = []  # 既存の担当製品をクリア
            
            for product_id in product_ids:
                product = Product.query.get_or_404(product_id)
                engineer.products.append(product)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '担当割り当てが正常に更新されました！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'エラーが発生しました: {str(e)}'}), 500

# シミュレーション
@app.route('/simulation')
def simulation():
    settings = Settings.query.first()
    simulations = Simulation.query.all()
    form = SimulationForm()
    return render_template('simulation.html', settings=settings, simulations=simulations, form=form)

@app.route('/simulation/run', methods=['POST'])
def run_simulation_route():
    form = SimulationForm()
    
    if form.validate_on_submit():
        # 新しいシミュレーションを保存
        simulation = Simulation(
            name=form.name.data,
            total_engineers_change=form.total_engineers_change.data,
            total_products_change=form.total_products_change.data,
            annual_inquiries_change=form.annual_inquiries_change.data,
            hours_per_inquiry_change=form.hours_per_inquiry_change.data,
            max_products_per_engineer_change=form.max_products_per_engineer_change.data,
            inquiry_work_ratio_change=form.inquiry_work_ratio_change.data
        )
        db.session.add(simulation)
        db.session.commit()
        
        # シミュレーション実行
        result = run_simulation(simulation.id)
        return jsonify(result)
    else:
        errors = {field: error for field, error in form.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400

@app.route('/simulation/get/<int:id>')
def get_simulation(id):
    simulation = Simulation.query.get_or_404(id)
    settings = Settings.query.first()
    
    # シミュレーション実行
    result = run_simulation(simulation.id)
    return jsonify(result)

@app.route('/simulation/delete/<int:id>', methods=['POST'])
def delete_simulation(id):
    simulation = Simulation.query.get_or_404(id)
    db.session.delete(simulation)
    db.session.commit()
    flash('シミュレーションが正常に削除されました！', 'success')
    return redirect(url_for('simulation'))

# 基本設定
@app.route('/settings')
def settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    
    form = SettingsForm(obj=settings)
    departments = Department.query.all()
    department_form = DepartmentForm()
    
    return render_template('settings.html', settings=settings, form=form, 
                          departments=departments, department_form=department_form, active_tab='settings')

@app.route('/settings/update', methods=['POST'])
def update_settings():
    settings = Settings.query.first()
    form = SettingsForm()
    
    if form.validate_on_submit():
        settings.min_engineers_per_product = form.min_engineers_per_product.data
        settings.max_products_per_engineer = form.max_products_per_engineer.data
        settings.hours_per_inquiry = form.hours_per_inquiry.data
        settings.inquiry_work_ratio = form.inquiry_work_ratio.data
        settings.work_hours_per_day = form.work_hours_per_day.data
        settings.work_days_per_year = form.work_days_per_year.data
        db.session.commit()
        flash('設定が正常に更新されました！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('settings'))

# API エンドポイント
@app.route('/api/dashboard/data')
def dashboard_data():
    settings = Settings.query.first()
    total_engineers = Engineer.query.count()
    total_products = Product.query.count()
    
    # 製品ごとの担当エンジニア数と充足率
    products_data = []
    for product in Product.query.all():
        engineer_count = product.engineers.count()
        required_engineers = calculate_staffing(product.annual_inquiries, settings)
        sufficiency_rate = min(100, (engineer_count / required_engineers) * 100) if required_engineers > 0 else 100
        
        products_data.append({
            'id': product.id,
            'name': product.name,
            'engineer_count': engineer_count,
            'annual_inquiries': product.annual_inquiries,
            'required_engineers': required_engineers,
            'sufficiency_rate': round(sufficiency_rate, 1)
        })
    
    # エンジニアごとの担当製品数、残業時間、負荷率
    engineers_data = []
    for engineer in Engineer.query.all():
        # 担当製品の稼働時間を計算
        total_workload = 0
        for product in engineer.products:
            assigned_engineers = product.engineers.count()
            product_workload = calculate_workload(product.annual_inquiries, settings) / assigned_engineers
            total_workload += product_workload
        
        # 年間稼働時間と残業時間を計算
        annual_work_hours = settings.work_hours_per_day * settings.work_days_per_year
        overtime_hours = max(0, total_workload - annual_work_hours)
        daily_overtime = overtime_hours / settings.work_days_per_year
        workload_percent = (total_workload / annual_work_hours) * 100
        
        engineers_data.append({
            'id': engineer.id,
            'name': engineer.name,
            'product_count': len(engineer.products),
            'total_workload': round(total_workload, 2),
            'annual_work_hours': annual_work_hours,
            'overtime_hours': round(overtime_hours, 2),
            'daily_overtime': round(daily_overtime, 2),
            'workload_percent': round(workload_percent, 1)
        })
    
    return jsonify({
        'total_engineers': total_engineers,
        'total_products': total_products,
        'products': products_data,
        'engineers': engineers_data
    })
