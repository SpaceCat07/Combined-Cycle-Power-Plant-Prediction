# Combined Cycle Power Plant Prediction App

Aplikasi web untuk memprediksi output daya pembangkit listrik Combined Cycle menggunakan model Random Forest. Aplikasi ini dibuat dengan Flask dan menyediakan interface yang user-friendly untuk melakukan prediksi, melihat riwayat, dan menganalisis data dengan chart.

## Features

- ✅ **Prediksi Power Output**: Input 4 parameter (Temperature, Ambient Pressure, Relative Humidity, Exhaust Vacuum) untuk prediksi
- ✅ **Sistem Login & Register**: Autentikasi user dengan password hashing 
- ✅ **Riwayat Prediksi**: Simpan dan lihat semua prediksi yang pernah dibuat
- ✅ **Dashboard Analytics**: Statistik dan overview prediksi user
- ✅ **Charts & Visualisasi**: Chart trend, scatter plot, correlation analysis
- ✅ **Export Data**: Download riwayat dalam format CSV/JSON
- ✅ **Responsive Design**: UI modern dengan Bootstrap 5

## Screenshots

### Landing Page
Halaman utama dengan informasi fitur dan demo account

### Dashboard
Overview statistik dan quick actions

### Prediction Form
Form input dengan validasi dan sample data

### History & Charts
Riwayat prediksi dengan pagination dan analytics charts

## Installation & Setup

### 1. Clone atau Download Project
```cmd
cd "d:\File Khan\Koolyeah\Sem 5\Data Mining\UAS PPD"
```

### 2. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 3. Siapkan Model Random Forest
Pastikan Anda memiliki file model Random Forest (.pkl) yang sudah dilatih dengan fitur:
- Temperature (AT): Ambient Temperature 
- Ambient Pressure (AP): Tekanan ambient
- Relative Humidity (RH): Kelembaban relatif
- Exhaust Vacuum (V): Vacuum exhaust

Letakkan file model dengan nama `model.pkl` di folder root project, atau upload via aplikasi web.

### 4. Jalankan Aplikasi
```cmd
python app.py
```

Aplikasi akan berjalan di: `http://localhost:5000`

## Quick Start

### Demo Account
Untuk mencoba aplikasi, gunakan:
- **Username**: demo
- **Password**: demo123

### Upload Model
1. Login ke aplikasi
2. Jika belum ada model, Anda akan diminta upload file .pkl
3. Model akan otomatis divalidasi dan siap digunakan

### Membuat Prediksi
1. Masuk ke halaman "Make Prediction"
2. Isi form dengan parameter:
   - **Temperature**: 1.81 - 37.11°C
   - **Ambient Pressure**: 992.89 - 1033.30 mbar
   - **Relative Humidity**: 25.56 - 100.16%
   - **Exhaust Vacuum**: 25.36 - 81.56 cm Hg
3. Klik "Predict Power Output"

### Sample Data
Gunakan sample data ini untuk testing:
```
Temperature: 14.96°C
Pressure: 1017.13 mbar  
Humidity: 73.17%
Vacuum: 62.39 cm Hg
```

## File Structure

```
├── app.py                 # Main Flask application
├── database.py            # Database operations & user management
├── ml_model.py            # Machine Learning model handler
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── combined_cycle.db      # SQLite database (auto-created)
├── model.pkl              # Your Random Forest model
├── scaler.pkl             # StandardScaler (optional)
└── templates/
    ├── base.html          # Base template layout
    ├── landing.html       # Landing page
    ├── login.html         # Login form
    ├── register.html      # Registration form  
    ├── dashboard.html     # User dashboard
    ├── predict.html       # Prediction form
    ├── history.html       # Prediction history
    └── charts.html        # Charts & analytics
```

## API Endpoints

- `GET /` - Landing page
- `GET /login` - Login form
- `POST /login` - Process login
- `GET /register` - Registration form
- `POST /register` - Process registration
- `GET /logout` - Logout
- `GET /dashboard` - User dashboard
- `GET /predict` - Prediction form
- `POST /predict` - Process prediction
- `GET /history` - Prediction history
- `GET /charts` - Analytics charts

## Database Schema

### Users Table
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password_hash (TEXT)
- created_at (TIMESTAMP)

### Predictions Table  
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- temperature (REAL)
- pressure (REAL)
- humidity (REAL)
- vacuum (REAL)
- power_output (REAL)
- created_at (TIMESTAMP)

## Technical Details

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLite dengan raw SQL queries
- **ML Library**: scikit-learn 1.3.0
- **Security**: Werkzeug password hashing

### Frontend
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.0.0
- **Charts**: Chart.js 3.9.1
- **Styling**: Custom CSS dengan gradients & animations

### Model Requirements
Model Random Forest harus:
- Dilatih dengan 4 fitur input sesuai urutan
- Output berupa nilai kontinyu (power output)
- Format pickle (.pkl) yang kompatibel dengan scikit-learn
- Opsional: StandardScaler untuk normalisasi input

## Customization

### Mengganti Model
1. Replace file `model.pkl` dengan model baru
2. Pastikan urutan fitur sama: [Temperature, Pressure, Humidity, Vacuum]
3. Restart aplikasi

### Styling
Edit file `templates/base.html` untuk mengubah:
- CSS custom di bagian `<style>` 
- Color scheme dengan mengubah CSS variables
- Animasi dan effects

### Database
Untuk database production, ubah connection di `database.py`:
```python
# Ganti SQLite dengan PostgreSQL/MySQL
conn = psycopg2.connect(database_url)
```

## Troubleshooting

### Model Loading Error
- Pastikan file `model.pkl` ada di root folder
- Check kompatibilitas scikit-learn version
- Pastikan model dilatih dengan 4 fitur input

### Import Error
- Install ulang dependencies: `pip install -r requirements.txt`
- Update pip: `python -m pip install --upgrade pip`

### Database Error
- Hapus file `combined_cycle.db` untuk reset database
- Check file permissions pada folder project

### Port Already in Use
```cmd
# Ganti port di app.py atau kill process
netstat -ano | findstr :5000
taskkill /pid <PID> /f
```

## License

Project ini dibuat untuk keperluan tugas UAS mata kuliah Data Mining. Silakan gunakan dan modifikasi sesuai kebutuhan pembelajaran.

## Contact

Jika ada pertanyaan atau masalah:
1. Check troubleshooting guide di atas
2. Pastikan semua dependencies terinstall
3. Verify model file format dan compatibility

---

**Happy Predicting! 🚀**