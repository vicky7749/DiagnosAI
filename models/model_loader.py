import joblib
import os

class ModelLoader:
    def __init__(self, models_dir='saved_models'):
        self.models_dir = models_dir
        self.ml_models = {}
        
    def load_ml_model(self, model_name):
        """Load machine learning models (Random Forest, etc.)"""
        model_path = os.path.join(self.models_dir, f'{model_name}_model.pkl')
        if os.path.exists(model_path):
            try:
                self.ml_models[model_name] = joblib.load(model_path)
                print(f"Loaded ML model: {model_name}")
                return True
            except Exception as e:
                print(f"Error loading ML model {model_name}: {e}")
        return False
    
    def get_ml_model(self, model_name):
        return self.ml_models.get(model_name)
    
    def load_all_models(self):
        """Load all available ML models"""
        ml_models = ['randomforest_diabetes', 'randomforest_cancer', 'randomforest_kidney']
        
        for model in ml_models:
            self.load_ml_model(model)