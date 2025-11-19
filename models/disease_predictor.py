import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class DiseasePredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize ML models for different diseases"""
        diseases = ['diabetes', 'covid', 'pneumonia', 'kidney_disease', 
                   'breast_cancer', 'alzheimer', 'brain_tumor', 'hepatitis_c']
        
        for disease in diseases:
            # Initialize appropriate models
            if disease in ['diabetes', 'covid', 'pneumonia', 'kidney_disease']:
                self.models[disease] = XGBClassifier(random_state=42, n_estimators=100)
            else:
                self.models[disease] = RandomForestClassifier(random_state=42, n_estimators=100)
            
            self.scalers[disease] = StandardScaler()
            
            # Train demo models with synthetic data
            self._train_demo_model(disease)
    
    def _train_demo_model(self, disease):
        """Create and train demo models with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        if disease == 'diabetes':
            X = np.column_stack([
                np.random.normal(50, 15, n_samples),  # age
                np.random.normal(120, 20, n_samples), # blood_pressure
                np.random.normal(100, 30, n_samples), # glucose
                np.random.normal(25, 5, n_samples),   # bmi
                np.random.poisson(1, n_samples),      # pregnancies
                np.random.normal(20, 10, n_samples),  # skin_thickness
                np.random.normal(80, 40, n_samples),  # insulin
                np.random.normal(0.5, 0.2, n_samples) # diabetes_pedigree
            ])
            # Create balanced labels with proper distribution
            risk_score = (X[:, 1] * 0.05 + X[:, 2] * 0.1 + np.random.normal(0, 0.5, n_samples))
            y = (risk_score > np.percentile(risk_score, 50)).astype(int)
            
        elif disease == 'covid':
            X = np.column_stack([
                np.random.exponential(2, n_samples),  # fever
                np.random.binomial(1, 0.5, n_samples), # cough
                np.random.binomial(1, 0.5, n_samples), # fatigue
                np.random.binomial(1, 0.4, n_samples), # breathing_difficulty
                np.random.binomial(1, 0.3, n_samples), # chest_pain
                np.random.binomial(1, 0.4, n_samples), # sore_throat
                np.random.binomial(1, 0.3, n_samples)  # loss_of_taste
            ])
            # Create balanced labels
            risk_score = (X[:, 0] * 0.2 + X[:, 1] * 0.3 + X[:, 2] * 0.2 + np.random.normal(0, 0.3, n_samples))
            y = (risk_score > np.percentile(risk_score, 60)).astype(int)
            
        elif disease == 'pneumonia':
            X = np.column_stack([
                np.random.exponential(1.5, n_samples),  # fever
                np.random.binomial(1, 0.6, n_samples),  # cough
                np.random.binomial(1, 0.4, n_samples),  # chest_pain
                np.random.binomial(1, 0.5, n_samples),  # breathing_difficulty
                np.random.binomial(1, 0.5, n_samples),  # fatigue
                np.random.binomial(1, 0.3, n_samples),  # sweating
                np.random.binomial(1, 0.4, n_samples)   # chills
            ])
            risk_score = (X[:, 0] * 0.3 + X[:, 1] * 0.2 + X[:, 2] * 0.2 + np.random.normal(0, 0.3, n_samples))
            y = (risk_score > np.percentile(risk_score, 55)).astype(int)
            
        elif disease == 'kidney_disease':
            X = np.column_stack([
                np.random.normal(50, 15, n_samples),    # age
                np.random.normal(120, 20, n_samples),   # blood_pressure
                np.random.normal(1.5, 0.5, n_samples),  # albumin
                np.random.normal(100, 30, n_samples),   # sugar
                np.random.binomial(1, 0.3, n_samples),  # red_blood_cells
                np.random.binomial(1, 0.4, n_samples),  # pus_cells
                np.random.normal(90, 25, n_samples)     # blood_glucose
            ])
            risk_score = (X[:, 0] * 0.05 + X[:, 1] * 0.05 + X[:, 2] * 0.3 + np.random.normal(0, 0.4, n_samples))
            y = (risk_score > np.percentile(risk_score, 50)).astype(int)
            
        else:
            # Generic model for other diseases with balanced classes
            n_features = len(self._get_feature_names(disease))
            X = np.random.normal(0, 1, (n_samples, n_features))
            coefficients = np.random.normal(0, 0.5, n_features)
            # Create balanced labels
            risk_score = X @ coefficients + np.random.normal(0, 0.5, n_samples)
            y = (risk_score > np.percentile(risk_score, 50)).astype(int)
        
        # Ensure we have both classes (0 and 1)
        unique_classes = np.unique(y)
        if len(unique_classes) == 1:
            # Force some diversity if we only have one class
            y[:n_samples//2] = 0
            y[n_samples//2:] = 1
            np.random.shuffle(y)
        
        print(f"Training {disease} - Classes: {np.unique(y)}, Counts: {np.bincount(y)}")
        
        X_scaled = self.scalers[disease].fit_transform(X)
        self.models[disease].fit(X_scaled, y)
        print(f"✓ Trained {disease} model - {np.sum(y)} positive, {len(y)-np.sum(y)} negative cases")
    
    def predict(self, disease_type, symptoms):
        """Predict disease based on symptoms"""
        try:
            if disease_type not in self.models:
                raise ValueError(f"Model for {disease_type} not found")
            
            # Convert symptoms to feature array
            feature_names = self._get_feature_names(disease_type)
            features = []
            
            for feature in feature_names:
                features.append(symptoms.get(feature, 0))
            
            features = np.array(features).reshape(1, -1)
            features_scaled = self.scalers[disease_type].transform(features)
            
            # Get prediction and probability
            prediction = self.models[disease_type].predict(features_scaled)[0]
            probability = self.models[disease_type].predict_proba(features_scaled)[0]
            
            confidence = max(probability)
            
            result_map = {
                'diabetes': ['No Diabetes', 'Diabetes Detected'],
                'covid': ['COVID Negative', 'COVID Positive'],
                'pneumonia': ['No Pneumonia', 'Pneumonia Detected'],
                'kidney_disease': ['Healthy Kidneys', 'Kidney Disease Detected'],
                'breast_cancer': ['Benign', 'Malignant Tumor'],
                'alzheimer': ['No Alzheimer', 'Alzheimer Detected'],
                'brain_tumor': ['No Tumor', 'Brain Tumor Detected'],
                'hepatitis_c': ['No Hepatitis C', 'Hepatitis C Detected']
            }
            
            prediction_text = result_map.get(disease_type, ['Negative', 'Positive'])[int(prediction)]
            
            return {
                'prediction': prediction_text,
                'confidence': round(confidence * 100, 2),
                'risk_level': 'High' if confidence > 0.7 else 'Medium' if confidence > 0.5 else 'Low'
            }
            
        except Exception as e:
            return {
                'prediction': 'Error in prediction',
                'confidence': 0.0,
                'risk_level': 'Unknown',
                'error': str(e)
            }
    
    def _get_feature_names(self, disease_type):
        """Get feature names for each disease type"""
        feature_map = {
            'diabetes': ['age', 'blood_pressure', 'glucose', 'bmi', 'pregnancies', 'skin_thickness', 'insulin', 'diabetes_pedigree'],
            'covid': ['fever', 'cough', 'fatigue', 'breathing_difficulty', 'chest_pain', 'sore_throat', 'loss_of_taste'],
            'pneumonia': ['fever', 'cough', 'chest_pain', 'breathing_difficulty', 'fatigue', 'sweating', 'chills'],
            'kidney_disease': ['age', 'blood_pressure', 'albumin', 'sugar', 'red_blood_cells', 'pus_cells', 'blood_glucose'],
            'breast_cancer': ['radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean', 'compactness_mean'],
            'alzheimer': ['age', 'memory_loss', 'cognitive_decline', 'behavior_changes', 'mri_findings', 'genetic_risk'],
            'brain_tumor': ['headaches', 'seizures', 'vision_problems', 'nausea', 'mri_abnormalities', 'speech_difficulty'],
            'hepatitis_c': ['fatigue', 'jaundice', 'abdominal_pain', 'nausea', 'liver_enzymes', 'bilirubin']
        }
        
        return feature_map.get(disease_type, [])