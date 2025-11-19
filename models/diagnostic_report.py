import sqlite3
from datetime import datetime

class DiagnosticReport:
    def __init__(self, id=None, disease_type=None, symptoms=None, prediction_result=None, 
                 confidence=None, risk_level=None, timestamp=None):
        self.id = id
        self.disease_type = disease_type
        self.symptoms = symptoms or {}
        self.prediction_result = prediction_result
        self.confidence = confidence
        self.risk_level = risk_level
        self.timestamp = timestamp or datetime.now()
    
    @staticmethod
    def create_table():
        """Create the diagnostic_reports table if it doesn't exist"""
        conn = sqlite3.connect('diagnosai.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_type TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                prediction_result TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save(self):
        """Save the report to database"""
        conn = sqlite3.connect('diagnosai.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostic_reports 
            (disease_type, symptoms, prediction_result, confidence, risk_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.disease_type,
            str(self.symptoms),
            self.prediction_result,
            self.confidence,
            self.risk_level,
            self.timestamp
        ))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id
    
    @staticmethod
    def get_all():
        """Get all diagnostic reports"""
        conn = sqlite3.connect('diagnosai.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, disease_type, symptoms, prediction_result, confidence, risk_level, timestamp
            FROM diagnostic_reports 
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            report = DiagnosticReport(
                id=row[0],
                disease_type=row[1],
                symptoms=eval(row[2]) if row[2] else {},
                prediction_result=row[3],
                confidence=row[4],
                risk_level=row[5],
                timestamp=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S') if row[6] else None
            )
            reports.append(report)
        return reports
    
    @staticmethod
    def get_by_id(report_id):
        """Get a report by ID"""
        conn = sqlite3.connect('diagnosai.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, disease_type, symptoms, prediction_result, confidence, risk_level, timestamp
            FROM diagnostic_reports 
            WHERE id = ?
        ''', (report_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DiagnosticReport(
                id=row[0],
                disease_type=row[1],
                symptoms=eval(row[2]) if row[2] else {},
                prediction_result=row[3],
                confidence=row[4],
                risk_level=row[5],
                timestamp=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S') if row[6] else None
            )
        return None

# Create table when module is imported
DiagnosticReport.create_table()