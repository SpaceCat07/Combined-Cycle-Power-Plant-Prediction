import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

class Database:
    def __init__(self, db_name='powerplant.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Membuat koneksi ke database SQLite"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Inisialisasi database dan tabel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel users untuk autentikasi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel predictions untuk menyimpan riwayat prediksi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                temperature REAL NOT NULL,
                ambient_pressure REAL NOT NULL,
                relative_humidity REAL NOT NULL,
                exhaust_vacuum REAL NOT NULL,
                predicted_power REAL NOT NULL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Buat user admin default jika belum ada
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
            cursor.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                ('admin', admin_hash, 'admin@powerplant.com')
            )
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, password, email=None):
        """Membuat user baru"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                (username, password_hash, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def verify_user(self, username, password):
        """Verifikasi login user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, password_hash FROM users WHERE username = ?',
            (username,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            return user[0]  # Return user ID
        return None
    
    def get_user_by_id(self, user_id):
        """Mendapatkan informasi user berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, username, email FROM users WHERE id = ?',
            (user_id,)
        )
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def save_prediction(self, user_id, temperature, ambient_pressure, relative_humidity, exhaust_vacuum, predicted_power):
        """Menyimpan hasil prediksi ke database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (user_id, temperature, ambient_pressure, relative_humidity, 
                                   exhaust_vacuum, predicted_power)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, temperature, ambient_pressure, relative_humidity, exhaust_vacuum, predicted_power))
        
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        return prediction_id
    
    def get_user_predictions(self, user_id, limit=None):
        """Mendapatkan riwayat prediksi user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, temperature, ambient_pressure, relative_humidity, 
                   exhaust_vacuum, predicted_power, prediction_date
            FROM predictions 
            WHERE user_id = ? 
            ORDER BY prediction_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id,))
        predictions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': p[0],
                'temperature': p[1],
                'ambient_pressure': p[2],
                'relative_humidity': p[3],
                'exhaust_vacuum': p[4],
                'predicted_power': p[5],
                'prediction_date': p[6]
            }
            for p in predictions
        ]
    
    def get_predictions_for_chart(self, user_id, limit=20):
        """Mendapatkan data prediksi untuk chart"""
        predictions = self.get_user_predictions(user_id, limit)
        
        # Reverse untuk menampilkan chronological order
        predictions = list(reversed(predictions))
        
        return {
            'dates': [p['prediction_date'][:16] for p in predictions],  # Format: YYYY-MM-DD HH:MM
            'power': [p['predicted_power'] for p in predictions],
            'temperature': [p['temperature'] for p in predictions],
            'pressure': [p['ambient_pressure'] for p in predictions],
            'humidity': [p['relative_humidity'] for p in predictions],
            'vacuum': [p['exhaust_vacuum'] for p in predictions]
        }
    
    def get_prediction_stats(self, user_id):
        """Mendapatkan statistik prediksi user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total,
                   AVG(predicted_power) as avg_power,
                   MIN(predicted_power) as min_power,
                   MAX(predicted_power) as max_power
            FROM predictions 
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats[0] > 0:
            return {
                'total_predictions': stats[0],
                'avg_power': round(stats[1], 2),
                'min_power': round(stats[2], 2),
                'max_power': round(stats[3], 2)
            }
        else:
            return {
                'total_predictions': 0,
                'avg_power': 0,
                'min_power': 0,
                'max_power': 0
            }