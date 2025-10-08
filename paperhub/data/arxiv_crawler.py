import arxiv
import PyPDF2
import requests
from pathlib import Path
import json

class ArxivCrawler:
    def __init__(self, save_dir="papers"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
    
    def search_papers(self, query, max_results=10, category=None):
        if category:
            query = f"cat:{category} AND {query}"
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate #최신 순으로 (수정)
        )
        
        papers = []
        
        # arxiv 라이브러리 문제
        try:
            results = search.results()
        except:
            results = search.get()
        
        for result in results: #크롤링하는 정보
            paper_info = {
                'id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'published': result.published.strftime('%Y-%m-%d'),
                'updated': result.updated.strftime('%Y-%m-%d'),
                'categories': result.categories,
                'pdf_url': result.pdf_url,
                'primary_category': result.primary_category
            }
            papers.append(paper_info)
            print(f"Found: {paper_info['title']}")
        
        return papers
    
    def download_pdf(self, paper_info):
        paper_id = paper_info['id']
        pdf_path = self.save_dir / f"{paper_id}.pdf"
        
        if pdf_path.exists():
            print(f"Already exists: {paper_id}")
            return str(pdf_path)
        
        try:
            print(f"Downloading: {paper_info['title']}")
            response = requests.get(paper_info['pdf_url'], timeout=30)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Saved: {pdf_path}")
            return str(pdf_path)
        
        except Exception as e:
            print(f"Error downloading {paper_id}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                max_pages = min(len(reader.pages), 50) #페이지수 제한 수정 필요
                
                for i in range(max_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text if text.strip() else None
        
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def save_metadata(self, papers, filename="papers_metadata.json"):
        metadata_path = self.save_dir / filename
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"\nMetadata saved: {metadata_path}")
        print(f"Total papers: {len(papers)}")
    
    def crawl_and_save(self, query, max_results=10, category=None, download_pdf=True):
        print(f"\n{'='*60}")
        print(f"Starting arXiv crawl")
        print(f"Query: {query}")
        print(f"Max results: {max_results}")
        print(f"{'='*60}\n")
        
        # 1. 논문 검색
        papers = self.search_papers(query, max_results, category)
        
        if not papers:
            print("Not found!")
            return []
        
        print(f"\nFound {len(papers)} papers")
        
        # 2. PDF 다운로드 및 텍스트 추출
        if download_pdf:
            print(f"\n{'='*60}")
            print("Downloading PDFs and extracting text")
            print(f"{'='*60}\n")
            
            for i, paper in enumerate(papers, 1):
                print(f"\n[{i}/{len(papers)}] Processing: {paper['title'][:60]}...")
                
                pdf_path = self.download_pdf(paper)
                
                if pdf_path:
                    paper['pdf_path'] = pdf_path
                    
                    # 텍스트 추출
                    text = self.extract_text_from_pdf(pdf_path)
                    if text:
                        paper['text'] = text
                        print(f"Text extracted: {len(text)} characters")
                    else:
                        print(f"Failed to extract text")
                        paper['text'] = paper['abstract']  # fallback to abstract
                else:
                    print(f"Failed to download PDF")
                    paper['text'] = paper['abstract']  # fallback to abstract
        
        # 3. 메타데이터 저장
        self.save_metadata(papers)
        
        return papers

if __name__ == "__main__":
    # 크롤러 초기화
    crawler = ArxivCrawler(save_dir="data")
    
    papers = crawler.crawl_and_save(
        query="large language model",
        max_results=30, #이거 수정하기(한 번에 몇 개 저장되는지)
        download_pdf=True
    )
    
    # papers = crawler.crawl_and_save(
    #     query="transformer",
    #     max_results=10,
    #     category="cs.CL",  # cs.AI, cs.LG, cs.CV
    #     download_pdf=True
    # )
    
    # 결과 요약 출력
    if papers:
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"{'='*60}")
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'][:2])}")
            print(f"   Published: {paper['published']}")
            has_text = 'text' in paper and paper['text']
            print(f"   Text extracted: {'✓' if has_text else '✗'}")
            if has_text:
                print(f"   Text length: {len(paper['text'])} chars")