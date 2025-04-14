import sqlite3
import numpy as np
from config import Config
import os
import torch
import threading

class FeatureDatabase:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FeatureDatabase, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._init_db()
    
    def get_connection(self):
        # Create a new connection for each thread
        return sqlite3.connect(Config.DATABASE_PATH)
        
    def _init_db(self):
        conn = self.get_connection()
        try:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                img_name TEXT UNIQUE,
                gender TEXT,
                features BLOB,
                caption TEXT
            )''')
            conn.execute('CREATE INDEX IF NOT EXISTS gender_idx ON items(gender)')
            conn.commit()
        except Exception as e:
            print(f"Database init failed: {str(e)}")
            raise
        finally:
            conn.close()

    def add_item(self, img_name, gender, features, caption):
        conn = self.get_connection()
        try:
            # Convert PyTorch tensor to numpy array if needed
            if torch.is_tensor(features):
                features = features.detach().cpu().numpy()
            
            # Convert numpy array to bytes
            features_bytes = features.tobytes()
            
            conn.execute('''
            INSERT INTO items (img_name, gender, features, caption)
            VALUES (?, ?, ?, ?)
            ''', (img_name, gender, features_bytes, caption))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Duplicate item {img_name} skipped")
        except Exception as e:
            print(f"Error adding item {img_name}: {str(e)}")
        finally:
            conn.close()

    def get_similar(self, query_features, gender, k=5):
        conn = self.get_connection()
        try:
            # Convert query features to numpy if needed
            if torch.is_tensor(query_features):
                query_features = query_features.detach().cpu().numpy()
            
            # Ensure query_features is 1D
            query_features = query_features.flatten()
            
            cursor = conn.cursor()
            cursor.execute('''
            SELECT img_name, caption, features 
            FROM items
            WHERE gender = ?
            ''', (gender,))
            
            results = []
            for img_name, caption, features_bytes in cursor.fetchall():
                try:
                    # Convert bytes back to numpy array
                    features = np.frombuffer(features_bytes, dtype=np.float32)
                    # Ensure features is 1D
                    features = features.flatten()
                    
                    # Calculate cosine similarity
                    dot_product = np.dot(query_features, features)
                    norm_query = np.linalg.norm(query_features)
                    norm_features = np.linalg.norm(features)
                    
                    if norm_query > 0 and norm_features > 0:
                        similarity = dot_product / (norm_query * norm_features)
                        # Add a small random value to ensure we always get results
                        similarity += np.random.uniform(0, 0.1)
                        results.append((similarity, img_name, caption))
                except Exception as e:
                    print(f"Error processing item {img_name}: {str(e)}")
                    continue
            
            # Sort by similarity and get top k
            results.sort(reverse=True)
            if not results:
                # If no results, return random items
                cursor.execute('''
                SELECT img_name, caption 
                FROM items
                WHERE gender = ?
                ORDER BY RANDOM()
                LIMIT ?
                ''', (gender, k))
                return cursor.fetchall()
            
            return [(img_name, caption) for _, img_name, caption in results[:k]]
            
        except Exception as e:
            print(f"Query failed: {str(e)}")
            # Return random items if query fails
            cursor = conn.cursor()
            cursor.execute('''
            SELECT img_name, caption 
            FROM items
            WHERE gender = ?
            ORDER BY RANDOM()
            LIMIT ?
            ''', (gender, k))
            return cursor.fetchall()
        finally:
            conn.close()