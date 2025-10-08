from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Paper(Base):
    __tablename__ = "papers"
    
    paper_id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, nullable=False)
    abstract = Column(Text, nullable=False)
    published_date = Column(Date, nullable=False)
    updated_date = Column(Date)
    categories = Column(JSON, nullable=False)
    primary_category = Column(String(50))
    pdf_url = Column(String(500))
    pdf_path = Column(String(500))
    # keywords = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<Paper(arxiv_id='{self.arxiv_id}', title='{self.title[:30]}...')>"
    
    def to_dict(self):
        return {
            "paper_id": self.paper_id,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None,
            "categories": self.categories,
            "primary_category": self.primary_category,
            "pdf_url": self.pdf_url,
            "pdf_path": self.pdf_path,
        }