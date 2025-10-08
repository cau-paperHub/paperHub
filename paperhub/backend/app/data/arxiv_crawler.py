import arxiv
import PyPDF2
import requests
from pathlib import Path
import json

class ArxivCrawler:
    def __init__(self, save_dir="papers"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
    
    def search_papers(self, query, max_results, category=None):
        if category:
            query = f"cat:{category} AND {query}"
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance #SubmittedDate, Relevance, LastUpdatedDate
        )
        
        papers = []
        
        try:
            results = search.results()
        except:
            results = search.get()
        
        for result in results:
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
        
        return papers
    
    def download_pdf(self, paper_info):
        paper_id = paper_info['id']
        pdf_path = self.save_dir / f"{paper_id}.pdf"
        
        if pdf_path.exists():
            return str(pdf_path)
        
        try:
            response = requests.get(paper_info['pdf_url'], timeout=30)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            return str(pdf_path)
        except Exception as e:
            return None
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                max_pages = min(len(reader.pages), 100)
                
                for i in range(max_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text if text.strip() else None
        except Exception as e:
            return None
    
    def save_metadata(self, papers, filename="papers_metadata.json"):
        metadata_path = self.save_dir / filename
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
    
    def crawl_and_save(self, query, max_results=10, category=None, download_pdf=True):
        papers = self.search_papers(query, max_results, category)
        
        if not papers:
            return []
        
        if download_pdf:
            for paper in papers:
                pdf_path = self.download_pdf(paper)
                
                if pdf_path:
                    paper['pdf_path'] = pdf_path
                    text = self.extract_text_from_pdf(pdf_path)
                    paper['text'] = text if text else paper['abstract']
                else:
                    paper['text'] = paper['abstract']
        
        self.save_metadata(papers)
        return papers