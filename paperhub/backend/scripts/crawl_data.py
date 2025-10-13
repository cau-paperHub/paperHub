import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.append(str(Path(__file__).parent.parent))

from app.data.arxiv_crawler import ArxivCrawler
from app.database import SessionLocal
from app.models.paper import Paper

def crawl_and_save_to_db(
    query, 
    max_results=50, 
    category=None, 
    download_pdf=False
):
    crawler = ArxivCrawler(save_dir="app/data/papers")
    
    print(f"Crawling papers for query: '{query}'")
    papers = crawler.crawl_and_save(
        query=query,
        max_results=max_results,
        category=category,
        download_pdf=download_pdf
    )
    
    if not papers:
        print("No papers found")
        return 0
    
    print(f"Found {len(papers)} papers")
    
    db = SessionLocal()
    saved_count = 0
    updated_count = 0
    skipped_count = 0
    
    try:
        for idx, paper_data in enumerate(papers, 1):
            arxiv_id = paper_data['id']
            
            existing_paper = db.query(Paper).filter(
                Paper.arxiv_id == arxiv_id
            ).first()
            
            try:
                published_date = datetime.strptime(
                    paper_data['published'], '%Y-%m-%d'
                ).date()
            except (KeyError, ValueError):
                skipped_count += 1
                continue
            
            try:
                updated_date = datetime.strptime(
                    paper_data['updated'], '%Y-%m-%d'
                ).date()
            except (KeyError, ValueError):
                updated_date = published_date
            
            try:
                if existing_paper:
                    existing_paper.title = paper_data['title']
                    existing_paper.authors = paper_data['authors']
                    existing_paper.abstract = paper_data['abstract']
                    existing_paper.updated_date = updated_date
                    existing_paper.categories = paper_data['categories']
                    existing_paper.primary_category = paper_data['primary_category']
                    
                    if 'pdf_path' in paper_data:
                        existing_paper.pdf_path = paper_data['pdf_path']
                    
                    updated_count += 1
                else:
                    new_paper = Paper(
                    arxiv_id=arxiv_id,
                    title=paper_data['title'],
                    authors=paper_data['authors'],
                    abstract=paper_data['abstract'],
                    published_date=published_date,
                    updated_date=updated_date,
                    categories=paper_data['categories'],
                    primary_category=paper_data['primary_category'],
                    pdf_url=paper_data['pdf_url'],
                    paper_id=None
                )
                    
                    db.add(new_paper)
                    saved_count += 1
            
            except Exception as e:
                print(f"Error processing paper {arxiv_id}: {e}")
                skipped_count += 1
                continue
        
        db.commit()
        print(f"Saved: {saved_count}, Updated: {updated_count}, Skipped: {skipped_count}")
        return saved_count
    
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def crawl_multiple_keywords(keywords, max_results_per_keyword=30):
    total_saved = 0
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n{'='*60}")
        print(f"Keyword {i}/{len(keywords)}: {keyword}")
        print(f"{'='*60}")
        
        try:
            saved = crawl_and_save_to_db(
                query=keyword,
                max_results=max_results_per_keyword,
                download_pdf=False
            )
            total_saved += saved
        except Exception as e:
            print(f"Failed to process keyword '{keyword}': {e}")
        
        if i < len(keywords):
            time.sleep(10)
    
    print(f"\n{'='*60}")
    print(f"Total papers saved: {total_saved}")
    print(f"{'='*60}")
    return total_saved

if __name__ == "__main__":
    # keywords = [
    #     "large language model",
    #     "transformer",
    #     "BERT",
    #     "GPT",
    #     "computer vision",
    #     "reinforcement learning",
    #     "deep learning",
    #     "llama",
    #     "recommendation"
    # ]
    
    # crawl_multiple_keywords(keywords, max_results_per_keyword=50)
    from app.database import init_db
    import json
    from pathlib import Path
    
    # 테이블 생성
    init_db()
    
    # JSON 파일에서 데이터 읽기
    json_path = Path("app/data/papers/papers_metadata.json")
    
    if json_path.exists():
        print("기존 JSON 파일을 DB에 저장합니다...")
        with open(json_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        db = SessionLocal()
        saved_count = 0
        skipped_count = 0
        
        try:
            for paper_data in papers:
                arxiv_id = paper_data['id']
                
                existing_paper = db.query(Paper).filter(
                    Paper.arxiv_id == arxiv_id
                ).first()
                
                if existing_paper:
                    continue
                
                try:
                    published_date = datetime.strptime(
                        paper_data['published'], '%Y-%m-%d'
                    ).date()
                except (KeyError, ValueError):
                    skipped_count += 1
                    continue
                
                try:
                    updated_date = datetime.strptime(
                        paper_data['updated'], '%Y-%m-%d'
                    ).date()
                except (KeyError, ValueError):
                    updated_date = published_date
                
                try:
                    new_paper = Paper(
                        arxiv_id=arxiv_id,
                        title=paper_data['title'],
                        authors=paper_data['authors'],
                        abstract=paper_data['abstract'],
                        published_date=published_date,
                        updated_date=updated_date,
                        categories=paper_data['categories'],
                        primary_category=paper_data['primary_category'],
                        pdf_url=paper_data['pdf_url'],
                        paper_id=None
                    )
                    db.add(new_paper)
                    saved_count += 1
                
                except Exception as e:
                    print(f"Error: {e}")
                    skipped_count += 1
            
            db.commit()
            print(f"✓ Saved: {saved_count}, Skipped: {skipped_count}")
        
        finally:
            db.close()
    else:
        print("JSON 파일을 찾을 수 없습니다!")