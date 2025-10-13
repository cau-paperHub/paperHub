from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional

from app.database import get_db
from app.models.paper import Paper

router = APIRouter(prefix="/papers", tags=["papers"])

@router.get("")
def get_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    sort_by: str = Query("published_date", regex="^(published_date|citation_cnt|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """논문 목록 조회"""
    query = db.query(Paper)
    
    if category:
        query = query.filter(Paper.primary_category == category)
    
    # 정렬
    sort_column = getattr(Paper, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    total = query.count()
    papers = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "papers": [paper.to_dict() for paper in papers]
    }

@router.get("/search")
def search_papers(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """제목 또는 초록으로 논문 검색"""
    query = db.query(Paper).filter(
        or_(
            Paper.title.ilike(f"%{q}%"),
            Paper.abstract.ilike(f"%{q}%")
        )
    ).order_by(Paper.published_date.desc())
    
    total = query.count()
    papers = query.offset(skip).limit(limit).all()
    
    return {
        "query": q,
        "total": total,
        "papers": [paper.to_dict() for paper in papers]
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """데이터베이스 통계"""
    total_papers = db.query(Paper).count()
    
    # 카테고리별 통계
    category_stats = db.query(
        Paper.primary_category,
        func.count(Paper.id)
    ).group_by(Paper.primary_category).order_by(
        func.count(Paper.id).desc()
    ).limit(10).all()
    
    # 최근 논문
    latest_paper = db.query(Paper).order_by(
        Paper.published_date.desc()
    ).first()
    
    return {
        "total_papers": total_papers,
        "categories": [
            {"category": cat, "count": count} 
            for cat, count in category_stats
        ],
        "latest_published": latest_paper.published_date.isoformat() if latest_paper else None
    }

@router.get("/{id}")
def get_paper(id: int, db: Session = Depends(get_db)):
    """논문 ID로 특정 논문 조회"""
    paper = db.query(Paper).filter(Paper.id == id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper.to_dict()

@router.get("/arxiv/{arxiv_id}")
def get_paper_by_arxiv_id(arxiv_id: str, db: Session = Depends(get_db)):
    """arXiv ID로 특정 논문 조회"""
    paper = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper.to_dict()