from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
from models.disease_predictor import DiseasePredictor
from models.diagnostic_report import DiagnosticReport

app = Flask(__name__)
app.config['SECRET_KEY'] = 'diagnosai-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/diagnosai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reports = db.relationship('DiagnosisReport', backref='user', lazy=True)

class DiagnosisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease_type = db.Column(db.String(100), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    prediction_result = db.Column(db.String(200), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize disease predictor
predictor = DiseasePredictor()

# Available diseases and their symptoms
DISEASES = {
    'diabetes': [
        'age', 'blood_pressure', 'glucose', 'bmi', 'pregnancies',
        'skin_thickness', 'insulin', 'diabetes_pedigree'
    ],
    'covid': [
        'fever', 'cough', 'fatigue', 'breathing_difficulty', 
        'chest_pain', 'sore_throat', 'loss_of_taste'
    ],
    'pneumonia': [
        'fever', 'cough', 'chest_pain', 'breathing_difficulty', 
        'fatigue', 'sweating', 'chills'
    ],
    'kidney_disease': [
        'age', 'blood_pressure', 'albumin', 'sugar', 
        'red_blood_cells', 'pus_cells', 'blood_glucose'
    ],
    'breast_cancer': [
        'radius_mean', 'texture_mean', 'perimeter_mean', 
        'area_mean', 'smoothness_mean', 'compactness_mean'
    ],
    'alzheimer': [
        'age', 'memory_loss', 'cognitive_decline', 
        'behavior_changes', 'mri_findings', 'genetic_risk'
    ],
    'brain_tumor': [
        'headaches', 'seizures', 'vision_problems', 
        'nausea', 'mri_abnormalities', 'speech_difficulty'
    ],
    'hepatitis_c': [
        'fatigue', 'jaundice', 'abdominal_pain', 
        'nausea', 'liver_enzymes', 'bilirubin'
    ]
}

@app.route('/')
def index():
    return render_template('index.html', diseases=DISEASES.keys())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Make sure DiagnosticReport is imported
    from models.diagnostic_report import DiagnosticReport
    
    user_reports = DiagnosticReport.get_all()
    
    # Calculate high risk reports
    high_risk_reports = [report for report in user_reports if hasattr(report, 'risk_level') and report.risk_level == 'High']
    
    return render_template('dashboard.html', 
                         reports=user_reports, 
                         high_risk_reports=high_risk_reports)
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        flash('Please login to use prediction features')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        disease_type = request.form['disease_type']
        symptoms = {}
        
        # Collect symptoms based on disease type
        for symptom in DISEASES[disease_type]:
            value = request.form.get(symptom, '0')
            try:
                symptoms[symptom] = float(value)
            except ValueError:
                symptoms[symptom] = 0.0
        
        # Get prediction
        result = predictor.predict(disease_type, symptoms)
        
        # Save report to database
        report = DiagnosisReport(
            user_id=session['user_id'],
            disease_type=disease_type,
            symptoms=json.dumps(symptoms),
            prediction_result=result['prediction'],
            confidence=result['confidence']
        )
        
        db.session.add(report)
        db.session.commit()
        
        return render_template('results.html', 
                             result=result, 
                             disease_type=disease_type,
                             symptoms=symptoms,
                             report_id=report.id)
    
    disease_type = request.args.get('disease', 'diabetes')
    return render_template('predict.html', 
                         disease_type=disease_type, 
                         diseases=DISEASES.keys(),
                         symptoms=DISEASES.get(disease_type, []))

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()
        disease_type = data.get('disease_type')
        symptoms = data.get('symptoms', {})
        
        result = predictor.predict(disease_type, symptoms)
        
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'risk_level': result['risk_level'],
            'disease_type': disease_type
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/report/<int:report_id>')
def view_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    report = DiagnosisReport.query.get_or_404(report_id)
    
    if report.user_id != session['user_id']:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    symptoms = json.loads(report.symptoms)
    return render_template('results.html', 
                         result={'prediction': report.prediction_result, 
                                'confidence': report.confidence,
                                'risk_level': 'High' if report.confidence > 70 else 'Medium' if report.confidence > 50 else 'Low'},
                         disease_type=report.disease_type,
                         symptoms=symptoms,
                         report_id=report.id,
                         from_history=True)

@app.route('/about')
def about():
    return render_template('about.html')

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    if not os.path.exists('database'):
        os.makedirs('database')
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)