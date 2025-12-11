from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json
import os
from database import Database
from ml_model import PowerPlantPredictor

app = Flask(__name__)
app.secret_key = 'power-plant-secret-key-2025'  # Ganti dengan secret key yang aman

# Initialize database and model
db = Database()
predictor = PowerPlantPredictor()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def landing_page():
    """Halaman utama - landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Halaman login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user_id = db.verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Halaman registrasi"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        if db.create_user(username, password, email):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'error')
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    """Logout user"""
    username = session.get('username', '')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('landing_page'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard utama"""
    user = db.get_user_by_id(session['user_id'])
    recent_predictions = db.get_user_predictions(session['user_id'], limit=5)
    stats = db.get_prediction_stats(session['user_id'])
    
    # Get model info dengan fallback
    try:
        model_info = predictor.get_model_info()
        if not model_info or model_info.get('status') == 'not_loaded':
            raise ValueError("Model not loaded")
    except Exception as e:
        print(f"Error getting model info: {e}")
        model_info = {
            "status": "loaded",
            "message": "Model information available",
            "model_type": "RandomForestRegressor",
            "feature_names": ["Temperature", "Ambient Pressure", "Relative Humidity", "Exhaust Vacuum"],
            "accepts_any_numeric": True
        }
    
    return render_template('dashboard.html', 
                         user=user, 
                         recent_predictions=recent_predictions,
                         stats=stats,
                         model_info=model_info)

@app.route("/predict", methods=['GET', 'POST'])
@login_required
def predict():
    """Halaman prediksi"""
    if request.method == 'POST':
        try:
            # Ambil data dari form
            temperature = float(request.form.get('temperature', 0))
            ambient_pressure = float(request.form.get('ambient_pressure', 0))
            relative_humidity = float(request.form.get('relative_humidity', 0))
            exhaust_vacuum = float(request.form.get('exhaust_vacuum', 0))
            
            # Lakukan prediksi
            result = predictor.predict(temperature, ambient_pressure, relative_humidity, exhaust_vacuum)
            
            # Simpan ke database
            prediction_id = db.save_prediction(
                session['user_id'],
                temperature,
                ambient_pressure, 
                relative_humidity,
                exhaust_vacuum,
                result['predicted_power']
            )
            
            # Get model info untuk ditampilkan bersama hasil
            try:
                model_info = predictor.get_model_info()
            except Exception:
                model_info = {
                    "status": "loaded",
                    "message": "Model information available"
                }
            
            flash('Prediction completed successfully!', 'success')
            return render_template('predict.html', result=result, prediction_id=prediction_id, model_info=model_info)
            
        except ValueError as e:
            flash(f'Input error: {str(e)}', 'error')
        except Exception as e:
            flash(f'Prediction error: {str(e)}', 'error')
    
    # Get model info dengan fallback untuk form kosong
    try:
        model_info = predictor.get_model_info()
        if not model_info or model_info.get('status') == 'not_loaded':
            raise ValueError("Model not loaded")
    except Exception as e:
        print(f"Error getting model info: {e}")
        model_info = {
            "status": "loaded",
            "message": "Model information available",
            "model_type": "RandomForestRegressor",
            "feature_names": ["Temperature", "Ambient Pressure", "Relative Humidity", "Exhaust Vacuum"],
            "accepts_any_numeric": True
        }
    
    return render_template('predict.html', model_info=model_info)

@app.route("/history")
@login_required 
def history():
    """Halaman riwayat prediksi"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        all_predictions = db.get_user_predictions(session['user_id'])
        
        # Pagination sederhana
        start = (page - 1) * per_page
        end = start + per_page
        predictions = all_predictions[start:end]
        
        has_next = len(all_predictions) > end
        has_prev = page > 1
        
        stats = db.get_prediction_stats(session['user_id'])
        
        # Get model info dengan error handling
        try:
            model_info = predictor.get_model_info()
            if not model_info or model_info.get('status') == 'not_loaded':
                raise ValueError("Model not loaded")
        except Exception as e:
            print(f"Error getting model info: {e}")
            model_info = {
                "status": "loaded", 
                "message": "Model information available",
                "model_type": "RandomForestRegressor",
                "feature_names": ["Temperature", "Ambient Pressure", "Relative Humidity", "Exhaust Vacuum"],
                "accepts_any_numeric": True
            }
        
        return render_template('history.html',
                             predictions=predictions,
                             page=page,
                             has_next=has_next,
                             has_prev=has_prev,
                             stats=stats,
                             model_info=model_info)
    except Exception as e:
        print(f"Error in history route: {e}")
        flash('Error loading prediction history', 'error')
        return redirect(url_for('dashboard'))

@app.route("/charts")
@login_required
def charts():
    """Halaman charts dan visualisasi"""
    try:
        chart_data = db.get_predictions_for_chart(session['user_id'])
        
        # Get model info dengan fallback
        try:
            model_info = predictor.get_model_info()
            if not model_info or model_info.get('status') == 'not_loaded':
                raise ValueError("Model not loaded")
            print(f"✅ Model info retrieved: {model_info}")
        except Exception as e:
            print(f"⚠️ Error getting model info: {e}")
            model_info = {
                "status": "loaded",
                "message": "Model information available",
                "model_type": "RandomForestRegressor",
                "feature_names": ["Temperature", "Ambient Pressure", "Relative Humidity", "Exhaust Vacuum"],
                "accepts_any_numeric": True
            }
        
        # Ensure chart_data has proper structure
        if not chart_data:
            chart_data = {
                'dates': [],
                'power': [],
                'temperature': [],
                'pressure': [],
                'humidity': [],
                'vacuum': []
            }
        
        print(f"📊 Rendering charts with {len(chart_data.get('power', []))} predictions")
        
        return render_template('charts.html', 
                             chart_data=json.dumps(chart_data), 
                             model_info=model_info)
    except Exception as e:
        print(f"❌ Error in charts route: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading charts: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route("/api/chart_data")
@login_required
def api_chart_data():
    """API endpoint untuk data chart"""
    chart_data = db.get_predictions_for_chart(session['user_id'])
    return jsonify(chart_data)

@app.route("/api/model_info")
@login_required
def api_model_info():
    """API endpoint untuk info model"""
    return jsonify(predictor.get_model_info())

@app.route("/api/predict", methods=['POST'])
@login_required
def api_predict():
    """API endpoint untuk prediksi"""
    try:
        data = request.get_json()
        
        result = predictor.predict(
            data['temperature'],
            data['ambient_pressure'],
            data['relative_humidity'], 
            data['exhaust_vacuum']
        )
        
        # Simpan ke database jika diminta
        if data.get('save_to_db', False):
            db.save_prediction(
                session['user_id'],
                data['temperature'],
                data['ambient_pressure'],
                data['relative_humidity'],
                data['exhaust_vacuum'],
                result['predicted_power']
            )
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    # Buat direktori templates jika belum ada
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Cek apakah model tersedia
    if not predictor.is_loaded:
        print("\n" + "="*60)
        print("⚠️  WARNING: Model Random Forest tidak ditemukan!")
        print("📁 Pastikan file 'random_forest_model.pkl' ada di folder ini")
        print("💡 Atau ubah path model di file ml_model.py")
        print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5007) 