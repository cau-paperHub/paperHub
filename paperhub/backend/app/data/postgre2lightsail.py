# app/data/postgre2lightsail.py
import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, declarative_base

LOCAL_DB_URL = "postgresql+psycopg2://user:password@localhost:5432/paperhub_db"
LIGHTSAIL_DB_URL = "postgresql+psycopg2://fastapi_user:fastapi-pass@localhost:15432/paperhub"

# 로컬 DB용 Base
LocalBase = declarative_base()

class LocalPaper(LocalBase):
    __tablename__ = "paper_info"
    
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, nullable=True)
    arxiv_id = Column(String(50), unique=True, index=True)
    title = Column(String(500))
    authors = Column(JSONB)
    abstract = Column(Text)
    published_date = Column(Date)
    updated_date = Column(Date)
    categories = Column(JSONB)
    primary_category = Column(String(50))
    pdf_url = Column(String(500))

LightsailBase = declarative_base()

class LightsailPaper(LightsailBase):
    __tablename__ = "paper_infos"
    __table_args__ = {'schema': 'core'}
    
    id = Column(BigInteger, primary_key=True)
    paper_id = Column(BigInteger, nullable=True, unique=True)
    arxiv_id = Column(String(255), unique=True, index=True)
    title = Column(String(255))
    authors = Column(JSONB)
    abstract_text = Column(Text)
    published_date = Column(Date)
    updated_date = Column(Date)
    categories = Column(JSONB)
    primary_category = Column(String(255))
    pdf_url = Column(String(255))

def migrate_papers():

    # 로컬 DB 연결
    source_engine = create_engine(LOCAL_DB_URL)
    SourceSession = sessionmaker(bind=source_engine)
    source_db = SourceSession()
    
    # Lightsail DB 연결
    target_engine = create_engine(LIGHTSAIL_DB_URL)
    TargetSession = sessionmaker(bind=target_engine)
    target_db = TargetSession()
    
    try:
        # 로컬 DB에서 조회 (LocalPaper 모델 사용)
        papers = source_db.query(LocalPaper).all()
        
        saved_count = 0
        skipped_count = 0
        
        for paper in papers:
            existing = target_db.query(LightsailPaper).filter(
                LightsailPaper.arxiv_id == paper.arxiv_id
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            new_paper = LightsailPaper(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                authors=paper.authors,
                abstract_text=paper.abstract,
                published_date=paper.published_date,
                updated_date=paper.updated_date,
                categories=paper.categories,
                primary_category=paper.primary_category,
                pdf_url=paper.pdf_url,
                paper_id=None
            )
            
            target_db.add(new_paper)
            saved_count += 1
            
            if saved_count % 100 == 0:
                target_db.commit()
                print(f"{saved_count}개 저장")
        
        target_db.commit()
        
    except Exception as e:
        print(f"error : {e}")
        import traceback
        traceback.print_exc()
        target_db.rollback()
        raise
    
    finally:
        source_db.close()
        target_db.close()

if __name__ == "__main__":
    migrate_papers()