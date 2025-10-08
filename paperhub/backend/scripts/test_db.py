import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))

from app.database import test_connection, init_db, engine

def check_tables():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        
        return [row[0] for row in result]

if __name__ == "__main__":
    if not test_connection():
        sys.exit(1)
    
    init_db()
    tables = check_tables()
    
    print(f"Database setup completed. Tables: {tables}")