import pickle
import numpy as np
import os
try:
    import joblib
except ImportError:
    joblib = None

class PowerPlantPredictor:
    def __init__(self, model_path='random_forest_model.pkl'):
        # Use absolute path
        if not os.path.isabs(model_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(current_dir, model_path)
        else:
            self.model_path = model_path
            
        self.model = None
        self.is_loaded = False
        self.feature_names = ['Temperature', 'Ambient Pressure', 'Relative Humidity', 'Exhaust Vacuum']
        
        # Load model saat inisialisasi
        self.load_model()
    
    def load_model(self):
        """Load model Random Forest dari file .pkl"""
        print(f"🔍 Mencoba memuat model dari: {self.model_path}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"📁 File exists: {os.path.exists(self.model_path)}")
        
        try:
            # Cek apakah file model ada
            if not os.path.exists(self.model_path):
                print(f"❌ File model tidak ditemukan: {self.model_path}")
                print(f"📁 Current working directory: {os.getcwd()}")
                print(f"📁 Script directory: {os.path.dirname(os.path.abspath(__file__))}")
                print("💡 Pastikan file 'random_forest_model.pkl' ada di folder yang sama dengan app.py")
                return False
            
            # Gunakan joblib langsung untuk kompatibilitas yang lebih baik dengan scikit-learn
            model_loaded = False
            
            # Coba joblib terlebih dahulu (lebih baik untuk scikit-learn models)
            if joblib is not None:
                try:
                    print("🔄 Loading model dengan joblib...")
                    self.model = joblib.load(self.model_path)
                    print(f"✅ Model berhasil dimuat dengan joblib dari: {self.model_path}")
                    model_loaded = True
                except Exception as joblib_error:
                    print(f"⚠️ Joblib gagal: {joblib_error}")
            
            # Jika joblib gagal atau tidak tersedia, coba pickle
            if not model_loaded:
                try:
                    print("🔄 Loading model dengan pickle...")
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    print(f"✅ Model berhasil dimuat dengan pickle dari: {self.model_path}")
                    model_loaded = True
                except Exception as pickle_error:
                    print(f"❌ Pickle juga gagal: {pickle_error}")
                    print("💡 Solusi: Upgrade scikit-learn ke versi 1.6.1")
                    print("   pip install scikit-learn==1.6.1")
                    return False
            
            if model_loaded:
                print(f"📊 Tipe model: {type(self.model).__name__}")
                
                # Cek apakah model adalah Random Forest
                if hasattr(self.model, 'n_estimators'):
                    print(f"🌳 Jumlah trees: {self.model.n_estimators}")
                
                print("✅ Model tidak menggunakan scaling - input langsung diproses")
                
                self.is_loaded = True
                return True
            
            return False
                
        except Exception as e:
            print(f"❌ Error saat memuat model: {e}")
            import traceback
            traceback.print_exc()
            return False
    

    
    def predict(self, temperature, ambient_pressure, relative_humidity, exhaust_vacuum):
        """Melakukan prediksi power output"""
        if not self.is_loaded or self.model is None:
            raise ValueError("Model belum dimuat. Pastikan file model tersedia.")
        
        # Validasi tipe data saja
        try:
            temperature = float(temperature)
            ambient_pressure = float(ambient_pressure)
            relative_humidity = float(relative_humidity)
            exhaust_vacuum = float(exhaust_vacuum)
        except (ValueError, TypeError):
            raise ValueError("Input harus berupa angka yang valid.")
        
        # Siapkan data input (tanpa scaling)
        input_data = np.array([[temperature, ambient_pressure, relative_humidity, exhaust_vacuum]])
        print(f"📥 Input: T={temperature}°C, AP={ambient_pressure}mbar, RH={relative_humidity}%, V={exhaust_vacuum}cm Hg")
        
        # Prediksi langsung tanpa scaling
        prediction = self.model.predict(input_data)[0]
        print(f"🔮 Prediction: {prediction:.2f} MW")
        
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
        """Validasi input parameters - hanya memeriksa tipe data"""
        try:
            float(temperature)
            float(ambient_pressure)
            float(relative_humidity)
            float(exhaust_vacuum)
            return True
        except (ValueError, TypeError):
            return False
    
    def get_model_info(self):
        """Mendapatkan informasi model"""
        if not self.is_loaded:
            return {"status": "not_loaded", "message": "Model belum dimuat"}
        
        info = {
            "status": "loaded",
            "model_type": type(self.model).__name__,
            "feature_names": self.feature_names,
            "accepts_any_numeric": True,
            "note": "Model dapat menerima nilai numerik apa saja"
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