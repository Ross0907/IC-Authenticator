"""
Database Manager Module
Handles storage and retrieval of analysis history
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class DatabaseManager:
    """
    Manages database for storing analysis history
    """
    
    def __init__(self, db_path='ic_authentication.db'):
        self.db_path = db_path
        self._initialize_database()
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return obj
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_path TEXT,
                part_number TEXT,
                manufacturer TEXT,
                is_authentic BOOLEAN,
                confidence REAL,
                extracted_data TEXT,
                official_data TEXT,
                verification_results TEXT,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_analyses INTEGER DEFAULT 0,
                authentic_count INTEGER DEFAULT 0,
                counterfeit_count INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, results: Dict):
        """Save analysis results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            extracted = results.get('extracted_markings', {})
            
            cursor.execute('''
                INSERT INTO analyses (
                    timestamp, image_path, part_number, manufacturer,
                    is_authentic, confidence, extracted_data, official_data,
                    verification_results, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                results.get('timestamp'),
                results.get('image_path'),
                extracted.get('part_number'),
                extracted.get('manufacturer'),
                bool(results.get('is_authentic')),
                float(results.get('confidence_score', 0)),
                json.dumps(self._convert_to_serializable(results.get('extracted_markings'))),
                json.dumps(self._convert_to_serializable(results.get('official_markings'))),
                json.dumps(self._convert_to_serializable(results.get('verification'))),
                results.get('recommendation')
            ))
            
            conn.commit()
            conn.close()
            
            # Update statistics
            self._update_statistics(results)
            
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    def _update_statistics(self, results: Dict):
        """Update daily statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            is_authentic = results.get('is_authentic', False)
            confidence = results.get('confidence_score', 0)
            
            # Check if today's record exists
            cursor.execute(
                'SELECT * FROM statistics WHERE date = ?',
                (today,)
            )
            
            if cursor.fetchone():
                # Update existing record
                if is_authentic:
                    cursor.execute('''
                        UPDATE statistics 
                        SET total_analyses = total_analyses + 1,
                            authentic_count = authentic_count + 1
                        WHERE date = ?
                    ''', (today,))
                else:
                    cursor.execute('''
                        UPDATE statistics 
                        SET total_analyses = total_analyses + 1,
                            counterfeit_count = counterfeit_count + 1
                        WHERE date = ?
                    ''', (today,))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO statistics (
                        date, total_analyses, authentic_count, counterfeit_count
                    ) VALUES (?, 1, ?, ?)
                ''', (
                    today,
                    1 if is_authentic else 0,
                    0 if is_authentic else 1
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Retrieve analysis history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM analyses 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'image_path': row['image_path'],
                    'part_number': row['part_number'],
                    'manufacturer': row['manufacturer'],
                    'is_authentic': bool(row['is_authentic']),
                    'confidence': row['confidence'],
                    'recommendation': row['recommendation']
                })
            
            return results
            
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict:
        """Get statistics for specified number of days"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM statistics 
                ORDER BY date DESC 
                LIMIT ?
            ''', (days,))
            
            rows = cursor.fetchall()
            conn.close()
            
            stats = {
                'daily': [],
                'total_analyses': 0,
                'total_authentic': 0,
                'total_counterfeit': 0,
                'authenticity_rate': 0.0
            }
            
            for row in rows:
                stats['daily'].append({
                    'date': row['date'],
                    'total': row['total_analyses'],
                    'authentic': row['authentic_count'],
                    'counterfeit': row['counterfeit_count']
                })
                
                stats['total_analyses'] += row['total_analyses']
                stats['total_authentic'] += row['authentic_count']
                stats['total_counterfeit'] += row['counterfeit_count']
            
            if stats['total_analyses'] > 0:
                stats['authenticity_rate'] = (
                    stats['total_authentic'] / stats['total_analyses'] * 100
                )
            
            return stats
            
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            return {}
    
    def search_by_part_number(self, part_number: str) -> List[Dict]:
        """Search analyses by part number"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM analyses 
                WHERE part_number LIKE ? 
                ORDER BY created_at DESC
            ''', (f'%{part_number}%',))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'part_number': row['part_number'],
                    'is_authentic': bool(row['is_authentic']),
                    'confidence': row['confidence']
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching database: {e}")
            return []
