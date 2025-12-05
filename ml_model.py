import pickle
import numpy as np
import os
from sklearn.preprocessing import StandardScaler

class PowerPlantPredictor:
    def __init__(self, model_path='random_forest_model.pkl', scaler_path=None):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.is_loaded = False
        self.feature_names = ['Temperature', 'Ambient Pressure', 'Relative Humidity', 'Exhaust Vacuum']
        
        # Load model saat inisialisasi
        self.load_model()
    
    def load_model(self):
        """Load model Random Forest dari file .pkl"""
        try:
            # Cek apakah file model ada
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                print(f"✅ Model berhasil dimuat dari: {self.model_path}")
                print(f"📊 Tipe model: {type(self.model).__name__}")
                
                # Cek apakah model adalah Random Forest
                if hasattr(self.model, 'n_estimators'):
                    print(f"🌳 Jumlah trees: {self.model.n_estimators}")
                
                # Load scaler jika ada
                if self.scaler_path and os.path.exists(self.scaler_path):
                    with open(self.scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    print(f"✅ Scaler dimuat dari: {self.scaler_path}")
                else:
                    # Buat scaler default jika tidak ada
                    self.create_default_scaler()
                
                self.is_loaded = True
                return True
            else:
                print(f"❌ File model tidak ditemukan: {self.model_path}")
                print("💡 Pastikan file 'random_forest_model.pkl' ada di folder yang sama dengan app.py")
                return False
                
        except Exception as e:
            print(f"❌ Error saat memuat model: {e}")
            return False
    
    def create_default_scaler(self):
        """Membuat scaler default berdasarkan rentang data power plant"""
        self.scaler = StandardScaler()
        
        # Data sampel untuk fitting scaler (rentang normal power plant)
        sample_data = np.array([
            [1.81, 992.89, 25.56, 25.36],    # Min values
            [37.11, 1033.30, 100.16, 81.56], # Max values
            [20.0, 1013.25, 67.5, 54.0],     # Typical values
            [25.0, 1020.0, 75.0, 60.0],      # Typical values
            [15.0, 1000.0, 50.0, 45.0]       # Typical values
        ])
        
        self.scaler.fit(sample_data)
        print("✅ Default scaler dibuat berdasarkan rentang data power plant")
    
    def predict(self, temperature, ambient_pressure, relative_humidity, exhaust_vacuum):
        """Melakukan prediksi power output"""
        if not self.is_loaded or self.model is None:
            raise ValueError("Model belum dimuat. Pastikan file model tersedia.")
        
        # Validasi input
        if not self.validate_inputs(temperature, ambient_pressure, relative_humidity, exhaust_vacuum):
            raise ValueError("Input tidak valid. Periksa rentang nilai yang dimasukkan.")
        
        # Siapkan data input
        input_data = np.array([[temperature, ambient_pressure, relative_humidity, exhaust_vacuum]])
        
        # Normalisasi jika ada scaler
        if self.scaler is not None:
            input_data = self.scaler.transform(input_data)
        
        # Prediksi
        prediction = self.model.predict(input_data)[0]
        
        # Hitung feature importance jika tersedia
        feature_importance = {}
        if hasattr(self.model, 'feature_importances_'):
            for i, feature in enumerate(self.feature_names):
                feature_importance[feature] = self.model.feature_importances_[i]
        
        return {
            'predicted_power': round(float(prediction), 2),
            'input_values': {
                'temperature': temperature,
                'ambient_pressure': ambient_pressure,
                'relative_humidity': relative_humidity,
                'exhaust_vacuum': exhaust_vacuum
            },
            'feature_importance': feature_importance
        }
    
    def validate_inputs(self, temperature, ambient_pressure, relative_humidity, exhaust_vacuum):
        """Validasi input parameters"""
        # Rentang nilai yang umum untuk Combined Cycle Power Plant
        temp_range = (1.81, 37.11)      # Celsius
        pressure_range = (992.89, 1033.30)  # mbar
        humidity_range = (25.56, 100.16)    # %
        vacuum_range = (25.36, 81.56)       # cm Hg
        
        if not (temp_range[0] <= temperature <= temp_range[1]):
            return False
        if not (pressure_range[0] <= ambient_pressure <= pressure_range[1]):
            return False
        if not (humidity_range[0] <= relative_humidity <= humidity_range[1]):
            return False
        if not (vacuum_range[0] <= exhaust_vacuum <= vacuum_range[1]):
            return False
        
        return True
    
    def get_model_info(self):
        """Mendapatkan informasi model"""
        if not self.is_loaded:
            return {"status": "not_loaded", "message": "Model belum dimuat"}
        
        info = {
            "status": "loaded",
            "model_type": type(self.model).__name__,
            "feature_names": self.feature_names,
            "input_ranges": {
                "Temperature": "1.81 - 37.11 °C",
                "Ambient Pressure": "992.89 - 1033.30 mbar", 
                "Relative Humidity": "25.56 - 100.16 %",
                "Exhaust Vacuum": "25.36 - 81.56 cm Hg"
            }
        }
        
        # Tambahkan info spesifik Random Forest
        if hasattr(self.model, 'n_estimators'):
            info['n_estimators'] = self.model.n_estimators
        
        if hasattr(self.model, 'feature_importances_'):
            info['feature_importance'] = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return info
    
    def batch_predict(self, data_list):
        """Prediksi batch untuk multiple input"""
        results = []
        for data in data_list:
            try:
                result = self.predict(
                    data['temperature'],
                    data['ambient_pressure'], 
                    data['relative_humidity'],
                    data['exhaust_vacuum']
                )
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        
        return results