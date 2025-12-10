import pickle
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
try:
    import joblib
except ImportError:
    joblib = None

class PowerPlantPredictor:
    def __init__(self, model_path='random_forest_model.pkl', scaler_path=None):
        # Use absolute path
        if not os.path.isabs(model_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(current_dir, model_path)
        else:
            self.model_path = model_path
            
        if scaler_path and not os.path.isabs(scaler_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.scaler_path = os.path.join(current_dir, scaler_path)
        else:
            self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.is_loaded = False
        self.use_scaling = None  # Auto-detect apakah perlu scaling
        self.feature_names = ['Temperature', 'Ambient Pressure', 'Relative Humidity', 'Exhaust Vacuum']
        
        # Load model saat inisialisasi
        self.load_model()
        
        # Auto-detect apakah model perlu scaling
        if self.is_loaded:
            self.detect_scaling_requirement()
    
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
            
            # Coba pickle dulu
            model_loaded = False
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✅ Model berhasil dimuat dengan pickle dari: {self.model_path}")
                model_loaded = True
            except Exception as pickle_error:
                print(f"⚠️ Pickle gagal: {pickle_error}")
                
                # Coba joblib sebagai fallback
                if joblib is not None:
                    try:
                        self.model = joblib.load(self.model_path)
                        print(f"✅ Model berhasil dimuat dengan joblib dari: {self.model_path}")
                        model_loaded = True
                    except Exception as joblib_error:
                        print(f"❌ Joblib juga gagal: {joblib_error}")
                        return False
                else:
                    print("❌ joblib tidak tersedia, install dengan: pip install joblib")
                    return False
            
            if model_loaded:
                print(f"📊 Tipe model: {type(self.model).__name__}")
                
                # Cek apakah model adalah Random Forest
                if hasattr(self.model, 'n_estimators'):
                    print(f"🌳 Jumlah trees: {self.model.n_estimators}")
                
                # Load scaler jika ada
                if self.scaler_path and os.path.exists(self.scaler_path):
                    try:
                        with open(self.scaler_path, 'rb') as f:
                            self.scaler = pickle.load(f)
                        print(f"✅ Scaler dimuat dari: {self.scaler_path}")
                    except Exception as scaler_error:
                        print(f"⚠️ Gagal memuat scaler: {scaler_error}")
                        self.create_default_scaler()
                else:
                    # Buat scaler default jika tidak ada
                    self.create_default_scaler()
                
                self.is_loaded = True
                return True
            
            return False
                
        except Exception as e:
            print(f"❌ Error saat memuat model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_default_scaler(self):
        """Dataset UCI tidak menggunakan normalisasi - data sudah dalam nilai asli"""
        # Data dari UCI Machine Learning Repository diberikan TANPA normalisasi
        # Model seharusnya dilatih dengan data raw, jadi kita tidak perlu scaler
        self.scaler = None
        print("✅ Dataset Combined Cycle Power Plant menggunakan data RAW (tanpa normalisasi)")
        print("   Temperature: 1.81 - 37.11°C")
        print("   Pressure: 992.89 - 1033.30 mbar") 
        print("   Humidity: 25.56 - 100.16%")
        print("   Vacuum: 25.36 - 81.56 cm Hg")
        print("   Output: 420.26 - 495.76 MW")
    
    def detect_scaling_requirement(self):
        """Auto-detect apakah model memerlukan input scaling atau tidak"""
        print("\n🔍 Auto-detecting scaling requirement...")
        
        # Test dengan data sample dari dataset UCI (nilai tengah range)
        test_samples = [
            [19.07, 1013.25, 67.87, 54.30],  # Sample 1: nilai tengah
            [25.0, 1020.0, 75.0, 60.0],       # Sample 2
            [15.0, 1000.0, 50.0, 45.0]        # Sample 3
        ]
        
        for i, sample in enumerate(test_samples):
            # Test tanpa scaling
            pred_raw = self.model.predict(np.array([sample]))[0]
            
            # Test dengan scaling
            scaler_temp = StandardScaler()
            scaler_temp.mean_ = np.array([19.65, 1013.26, 73.31, 54.31])
            scaler_temp.scale_ = np.array([7.45, 5.94, 14.60, 12.71])
            scaler_temp.var_ = scaler_temp.scale_ ** 2
            scaler_temp.n_features_in_ = 4
            
            sample_scaled = scaler_temp.transform(np.array([sample]))
            pred_scaled = self.model.predict(sample_scaled)[0]
            
            print(f"   Sample {i+1}: Raw={pred_raw:.2f} MW, Scaled={pred_scaled:.2f} MW")
        
        # Hitung rata-rata untuk menentukan mana yang lebih masuk akal
        preds_raw = [self.model.predict(np.array([s]))[0] for s in test_samples]
        
        scaler_temp = StandardScaler()
        scaler_temp.mean_ = np.array([19.65, 1013.26, 73.31, 54.31])
        scaler_temp.scale_ = np.array([7.45, 5.94, 14.60, 12.71])
        scaler_temp.var_ = scaler_temp.scale_ ** 2
        scaler_temp.n_features_in_ = 4
        
        preds_scaled = [self.model.predict(scaler_temp.transform(np.array([s])))[0] for s in test_samples]
        
        avg_raw = np.mean(preds_raw)
        avg_scaled = np.mean(preds_scaled)
        std_raw = np.std(preds_raw)
        std_scaled = np.std(preds_scaled)
        
        print(f"\n   📊 Raw predictions - Mean: {avg_raw:.2f}, Std: {std_raw:.2f}")
        print(f"   📊 Scaled predictions - Mean: {avg_scaled:.2f}, Std: {std_scaled:.2f}")
        
        # Expected range: 420-496 MW
        # Jika raw predictions dalam range dan punya variance, gunakan raw
        # Jika scaled predictions lebih masuk akal, gunakan scaled
        
        raw_in_range = all(420 <= p <= 500 for p in preds_raw)
        scaled_in_range = all(420 <= p <= 500 for p in preds_scaled)
        
        if raw_in_range and std_raw > 1:
            self.use_scaling = False
            self.scaler = None
            print("   ✅ Decision: Model menggunakan RAW input (tanpa scaling)")
        elif scaled_in_range and std_scaled > 1:
            self.use_scaling = True
            self.scaler = scaler_temp
            print("   ✅ Decision: Model menggunakan SCALED input (dengan normalisasi)")
        elif std_raw > std_scaled:
            self.use_scaling = False
            self.scaler = None
            print("   ✅ Decision: Raw input (variance lebih tinggi = lebih responsive)")
        else:
            self.use_scaling = True
            self.scaler = scaler_temp
            print("   ✅ Decision: Scaled input (prediksi lebih stabil)")
    
    
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
        
        # Siapkan data input
        input_data = np.array([[temperature, ambient_pressure, relative_humidity, exhaust_vacuum]])
        print(f"📥 Input: T={temperature}°C, AP={ambient_pressure}mbar, RH={relative_humidity}%, V={exhaust_vacuum}cm Hg")
        
        # Gunakan metode yang sudah di-detect saat inisialisasi
        if self.use_scaling and self.scaler is not None:
            input_data_processed = self.scaler.transform(input_data)
            print(f"   Using SCALED input: {input_data_processed}")
        else:
            input_data_processed = input_data
            print(f"   Using RAW input: {input_data_processed}")
        
        # Prediksi
        prediction = self.model.predict(input_data_processed)[0]
        print(f"🔮 Prediction: {prediction:.2f} MW")
        
        # Validasi hasil
        if not (420 <= prediction <= 500):
            print(f"⚠️ WARNING: Prediction di luar range normal (420-496 MW)")
        
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