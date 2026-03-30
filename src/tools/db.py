import sqlite3
from datetime import datetime
import os

# Create DB file securely in the root of the project
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "equity_desk.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            asset_type TEXT,
            final_score REAL,
            recommendation TEXT,
            fundamental_score REAL,
            technical_score REAL,
            sentiment_score REAL,
            pm_summary TEXT
        )
    ''')
    
    # Safely inject the additional JSON column for caching metrics
    try:
        cursor.execute("ALTER TABLE analysis_logs ADD COLUMN fundamental_data_json TEXT")
    except sqlite3.OperationalError:
        pass # Has already been created
        
    # Table for pure query text caching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_cache (
            query_text TEXT PRIMARY KEY,
            ticker TEXT,
            asset_type TEXT,
            reply TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[SQLite Caching Layer] Database tables loaded securely at {DB_PATH}")

def get_cached_query(query_text: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        normalized_query = query_text.strip().lower()
        cursor.execute("SELECT ticker, asset_type, reply FROM query_cache WHERE query_text = ?", (normalized_query,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            print(f"[Cache HIt] Bypassed Intent LLM for query: '{query_text}'")
            return dict(row)
    except Exception as e:
        print(f"[Cache Error] get_cached_query: {e}")
    return None

def insert_cached_query(query_text: str, ticker: str, asset_type: str, reply: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        normalized_query = query_text.strip().lower()
        cursor.execute('''
            INSERT OR REPLACE INTO query_cache (query_text, ticker, asset_type, reply)
            VALUES (?, ?, ?, ?)
        ''', (normalized_query, ticker, asset_type, reply))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Cache Error] insert_cached_query: {e}")

def get_recent_analysis(ticker: str):
    """Retrieves the analysis payload directly from SQLite if analyzed under 12 hours ago."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_logs 
            WHERE ticker = ? 
            ORDER BY datetime(timestamp) DESC 
            LIMIT 1
        ''', (ticker.upper(),))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # TTL threshold 12 hrs
            ts = datetime.fromisoformat(row['timestamp'])
            hours_diff = (datetime.now() - ts).total_seconds() / 3600
            if hours_diff < 12.0:
                print(f"[Cache Hit] Bypassed LangGraph -> DB Pull for {ticker}")
                return dict(row)
    except Exception as e:
        print(f"[Cache Error] get_recent_analysis: {e}")
    return None

def insert_analysis(data: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        import json
        fund_json = json.dumps(data.get("fundamental_data", {}))
        
        cursor.execute('''
            INSERT INTO analysis_logs (
                timestamp, ticker, asset_type, final_score, recommendation, 
                fundamental_score, technical_score, sentiment_score, pm_summary, fundamental_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data.get("ticker", "").upper(),
            data.get("asset_type"),
            data.get("final_score", 0.0),
            data.get("recommendation", "N/A"),
            data.get("fundamental_score", 0.0),
            data.get("technical_score", 0.0),
            data.get("sentiment_score", 0.0),
            data.get("final_summary", "No summary generated."),
            fund_json
        ))
        conn.commit()
        conn.close()
        print(f"[SQLite Caching Layer] Persisted {data.get('ticker')} correctly.")
    except Exception as e:
        print(f"[SQLite Caching Layer] Failed to insert log: {e}")
