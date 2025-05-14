from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Engineer, Product, Assignment, Parameter
from sqlalchemy import func
import json
from utils import generate_demo_data, calculate_dashboard_metrics, calculate_simulation_results

# Dashboard route
@app.route('/')
def dashboard():
    try:
        metrics = calculate_dashboard_metrics()
        return render_template('dashboard.html', metrics=metrics)
    except Exception as e:
        app.logger.error(f"ダッシュボード表示エラー: {str(e)}")
        # エラー時は基本情報のみ表示
        engineer_count = db.session.query(func.count(Engineer.id)).scalar()
        product_count = db.session.query(func.count(Product.id)).scalar()
        assignment_count = db.session.query(func.count(Assignment.id)).scalar()
        
        metrics = {
            'summary': {
                'engineer_count': engineer_count,
                'product_count': product_count,
                'total_annual_inquiries': 0,
                'avg_products_per_engineer': round(assignment_count / max(1, engineer_count), 1),
                'avg_engineers_per_product': round(assignment_count / max(1, product_count), 1),
                'overloaded_engineers': 0,
                'understaffed_products': 0,
                'high_overtime_engineers': 0
            },
            'engineers': [],
            'products': []
        }
        return render_template('dashboard.html', metrics=metrics)

# Engineers routes
@app.route('/engineers')
def engineers():
    engineers_list = Engineer.query.all()
    return render_template('engineers.html', engineers=engineers_list)

@app.route('/engineers/add', methods=['POST'])
def add_engineer():
    name = request.form.get('name')
    department = request.form.get('department')
    
    if not name or not department:
        flash('エンジニア名と所属課名は必須です。', 'danger')
        return redirect(url_for('engineers'))
    
    new_engineer = Engineer(name=name, department=department)
    db.session.add(new_engineer)
    db.session.commit()
    
    flash('エンジニアが正常に追加されました。', 'success')
    return redirect(url_for('engineers'))

@app.route('/engineers/edit/<int:id>', methods=['POST'])
def edit_engineer(id):
    engineer = Engineer.query.get_or_404(id)
    
    engineer.name = request.form.get('name')
    engineer.department = request.form.get('department')
    
    if not engineer.name or not engineer.department:
        flash('エンジニア名と所属課名は必須です。', 'danger')
        return redirect(url_for('engineers'))
    
    db.session.commit()
    
    flash('エンジニア情報が正常に更新されました。', 'success')
    return redirect(url_for('engineers'))

@app.route('/engineers/delete/<int:id>', methods=['POST'])
def delete_engineer(id):
    engineer = Engineer.query.get_or_404(id)
    db.session.delete(engineer)
    db.session.commit()
    
    flash('エンジニアが正常に削除されました。', 'success')
    return redirect(url_for('engineers'))

# Products routes
@app.route('/products')
def products():
    products_list = Product.query.all()
    return render_template('products.html', products=products_list)

@app.route('/products/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    vendor = request.form.get('vendor')
    annual_inquiries = request.form.get('annual_inquiries', 0, type=int)
    
    if not name or not vendor:
        flash('製品名とベンダー名は必須です。', 'danger')
        return redirect(url_for('products'))
    
    new_product = Product(name=name, vendor=vendor, annual_inquiries=annual_inquiries)
    db.session.add(new_product)
    db.session.commit()
    
    flash('製品が正常に追加されました。', 'success')
    return redirect(url_for('products'))

@app.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    product.name = request.form.get('name')
    product.vendor = request.form.get('vendor')
    product.annual_inquiries = request.form.get('annual_inquiries', 0, type=int)
    
    if not product.name or not product.vendor:
        flash('製品名とベンダー名は必須です。', 'danger')
        return redirect(url_for('products'))
    
    db.session.commit()
    
    flash('製品情報が正常に更新されました。', 'success')
    return redirect(url_for('products'))

@app.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    flash('製品が正常に削除されました。', 'success')
    return redirect(url_for('products'))

# Assignments routes
@app.route('/assignments')
def assignments():
    engineers_list = Engineer.query.order_by(Engineer.name).all()
    products_list = Product.query.order_by(Product.name).all()
    
    # Get assignment counts for each engineer
    engineer_assignments = {}
    for engineer in engineers_list:
        engineer_assignments[engineer.id] = len(engineer.assignments)
    
    # Get assignment counts for each product
    product_assignments = {}
    for product in products_list:
        product_assignments[product.id] = len(product.assignments)
    
    # Get all current assignments
    all_assignments = Assignment.query.all()
    
    # Create a set of (engineer_id, product_id) tuples for quick lookup
    assignment_set = {(a.engineer_id, a.product_id) for a in all_assignments}
    
    return render_template(
        'assignments.html', 
        engineers=engineers_list, 
        products=products_list,
        engineer_assignments=engineer_assignments,
        product_assignments=product_assignments,
        assignment_set=assignment_set
    )

@app.route('/assignments/update', methods=['POST'])
def update_assignments():
    data = request.json
    engineer_id = data.get('engineer_id')
    product_id = data.get('product_id')
    is_assigned = data.get('is_assigned')
    
    if not engineer_id or not product_id:
        return jsonify({'success': False, 'error': '有効なエンジニアIDと製品IDが必要です。'})
    
    # Check if the assignment exists
    assignment = Assignment.query.filter_by(
        engineer_id=engineer_id, 
        product_id=product_id
    ).first()
    
    if is_assigned and not assignment:
        # Create new assignment
        new_assignment = Assignment(
            engineer_id=engineer_id,
            product_id=product_id
        )
        db.session.add(new_assignment)
        db.session.commit()
        return jsonify({'success': True, 'message': '担当割り当てが追加されました。'})
    
    elif not is_assigned and assignment:
        # Remove assignment
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'success': True, 'message': '担当割り当てが削除されました。'})
    
    return jsonify({'success': True, 'message': '変更はありませんでした。'})

# Simulation route
@app.route('/simulation')
def simulation():
    params = {p.key: p.value for p in Parameter.query.all()}
    return render_template('simulation.html', params=params)

@app.route('/simulation/run', methods=['POST'])
def run_simulation():
    data = request.json
    results = calculate_simulation_results(data)
    return jsonify(results)

# Parameters route
@app.route('/parameters')
def parameters():
    params = Parameter.query.all()
    departments = db.session.query(Engineer.department).distinct().all()
    departments = [d[0] for d in departments]
    return render_template('parameters.html', params=params, departments=departments)

@app.route('/parameters/update', methods=['POST'])
def update_parameters():
    for key, value in request.form.items():
        if key.startswith('param_'):
            param_key = key[6:]  # Remove 'param_' prefix
            param = Parameter.query.filter_by(key=param_key).first()
            if param:
                param.value = value
    
    db.session.commit()
    flash('パラメータが正常に更新されました。', 'success')
    return redirect(url_for('parameters'))

# API routes for AJAX calls
@app.route('/api/dashboard/data')
def dashboard_data():
    try:
        metrics = calculate_dashboard_metrics()
        return jsonify(metrics)
    except Exception as e:
        app.logger.error(f"ダッシュボード API エラー: {str(e)}")
        # エラー発生時も最低限の情報を返す
        engineer_count = db.session.query(func.count(Engineer.id)).scalar()
        product_count = db.session.query(func.count(Product.id)).scalar()
        assignment_count = db.session.query(func.count(Assignment.id)).scalar()
        
        error_metrics = {
            'summary': {
                'engineer_count': engineer_count,
                'product_count': product_count,
                'total_annual_inquiries': 0,
                'avg_products_per_engineer': round(assignment_count / max(1, engineer_count), 1),
                'avg_engineers_per_product': round(assignment_count / max(1, product_count), 1),
                'overloaded_engineers': 0,
                'understaffed_products': 0,
                'high_overtime_engineers': 0
            },
            'engineers': [],
            'products': [],
            'error': str(e)
        }
        return jsonify(error_metrics)

@app.route('/api/generate_demo_data', methods=['POST'])
def api_generate_demo_data():
    try:
        # Clear existing data
        Assignment.query.delete()
        Engineer.query.delete()
        Product.query.delete()
        db.session.commit()
        
        # Generate new demo data
        generate_demo_data()
        
        return jsonify({'success': True, 'message': 'デモデータが正常に生成されました。'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'エラーが発生しました: {str(e)}'})
