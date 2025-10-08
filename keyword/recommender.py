#읽은 논문에 대한 표시가 필요함

import json
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class PaperRecommender:
    def __init__(self, api_key: str, index_name: str = "paper-keywords"):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def recommend_by_paper_id(self, paper_id: str, top_k: int = 5) -> List[Dict]:
        """
        특정 논문과 유사한 논문 추천
        (사용자가 읽은 논문을 기반으로)
        """
        # 해당 논문의 벡터 가져오기
        result = self.index.fetch(ids=[paper_id])
        
        vectors = result.vectors if hasattr(result, 'vectors') else result.get('vectors', {})
        
        if paper_id not in vectors:
            print(f"Paper {paper_id} not found in index")
            return []
        
        paper_vector = vectors[paper_id].values if hasattr(vectors[paper_id], 'values') else vectors[paper_id]['values']
        
        # 유사한 논문 검색 (자기 자신 제외)
        similar = self.index.query(
            vector=paper_vector,
            top_k=top_k + 1,  # 자기 자신도 포함되므로 +1
            include_metadata=True
        )
        
        # 최신 버전 호환
        matches = similar.matches if hasattr(similar, 'matches') else similar.get('matches', [])
        
        # 자기 자신 제외
        recommendations = [m for m in matches if m.id != paper_id][:top_k]
        
        return recommendations
    
    def recommend_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict]:
        """
        키워드 기반 논문 추천
        """
        # 키워드를 임베딩으로 변환
        keyword_text = ", ".join(keywords)
        embedding = self.embedding_model.encode(keyword_text).tolist()
        
        # 유사한 논문 검색
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # 최신 버전 호환
        matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
        
        return matches
    
    def recommend_by_user_history(self, read_paper_ids: List[str], top_k: int = 10) -> List[Dict]:
        """
        사용자가 읽은 여러 논문을 기반으로 추천
        """
        if not read_paper_ids:
            return []
        
        # 읽은 논문들의 벡터 가져오기
        result = self.index.fetch(ids=read_paper_ids)
        
        # 최신 버전 호환
        vectors_dict = result.vectors if hasattr(result, 'vectors') else result.get('vectors', {})
        
        vectors = []
        for paper_id in read_paper_ids:
            if paper_id in vectors_dict:
                vec = vectors_dict[paper_id]
                vec_values = vec.values if hasattr(vec, 'values') else vec['values']
                vectors.append(vec_values)
        
        if not vectors:
            return []
        
        # 벡터들의 평균 계산 (사용자 프로필)
        import numpy as np
        avg_vector = np.mean(vectors, axis=0).tolist()
        
        # 유사한 논문 검색
        similar = self.index.query(
            vector=avg_vector,
            top_k=top_k + len(read_paper_ids),  # 읽은 논문들도 포함될 수 있으므로
            include_metadata=True
        )
        
        # 최신 버전 호환
        matches = similar.matches if hasattr(similar, 'matches') else similar.get('matches', [])
        
        # 이미 읽은 논문 제외
        recommendations = [
            m for m in matches 
            if (m.id if hasattr(m, 'id') else m['id']) not in read_paper_ids
        ][:top_k]
        
        return recommendations
    
    def recommend_by_highlights(self, highlight_texts: List[str], top_k: int = 5) -> List[Dict]:
        """
        사용자가 하이라이트한 텍스트 기반 추천
        (메모/하이라이트 내용 활용)
        """
        # 하이라이트 텍스트들을 결합
        combined_text = " ".join(highlight_texts)
        
        # 임베딩 생성
        embedding = self.embedding_model.encode(combined_text).tolist()
        
        # 유사한 논문 검색
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # 최신 버전 호환
        matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
        
        return matches
    
    def hybrid_recommendation(self, 
                             read_paper_ids: List[str] = None,
                             keywords: List[str] = None,
                             highlight_texts: List[str] = None,
                             top_k: int = 10) -> List[Dict]:
        """
        여러 feature 조합
        - 읽은 논문
        - 검색 키워드  
        - 하이라이트 내용
        """
        import numpy as np
        
        all_vectors = []
        weights = []
        
        # 1. 읽은 논문 기반 벡터
        if read_paper_ids:
            result = self.index.fetch(ids=read_paper_ids)
            vectors_dict = result.vectors if hasattr(result, 'vectors') else result.get('vectors', {})
            
            for paper_id in read_paper_ids:
                if paper_id in vectors_dict:
                    vec = vectors_dict[paper_id]
                    vec_values = vec.values if hasattr(vec, 'values') else vec['values']
                    all_vectors.append(vec_values)
                    weights.append(2.0)  # 읽은 논문에 높은 가중치
        
        # 2. 키워드 기반 벡터
        if keywords:
            keyword_text = ", ".join(keywords)
            embedding = self.embedding_model.encode(keyword_text).tolist()
            all_vectors.append(embedding)
            weights.append(1.5)
        
        # 3. 하이라이트 기반 벡터
        if highlight_texts:
            combined_text = " ".join(highlight_texts)
            embedding = self.embedding_model.encode(combined_text).tolist()
            all_vectors.append(embedding)
            weights.append(2.5)  # 하이라이트에 가장 높은 가중치
        
        if not all_vectors:
            return []
        
        # 가중 평균 계산
        weights = np.array(weights)
        weights = weights / weights.sum()  # 정규화
        
        weighted_vector = np.average(all_vectors, axis=0, weights=weights).tolist()
        
        # 유사한 논문 검색
        similar = self.index.query(
            vector=weighted_vector,
            top_k=top_k + (len(read_paper_ids) if read_paper_ids else 0),
            include_metadata=True
        )
        
        # 최신 버전 호환
        matches = similar.matches if hasattr(similar, 'matches') else similar.get('matches', [])
        
        # 이미 읽은 논문 제외
        exclude_ids = set(read_paper_ids) if read_paper_ids else set()
        recommendations = [
            m for m in matches 
            if (m.id if hasattr(m, 'id') else m['id']) not in exclude_ids
        ][:top_k]
        
        return recommendations


# 사용 예시
if __name__ == "__main__":
    recommender = PaperRecommender(
        api_key="pcsk_4N174X_M87YqzLwgiiW79HgaqaS3o9jFGX5bwn7ZeM36UQwDWreqtUg8RkMwtWMiC42y2B",
        index_name="paper-keywords"
    )
    
    print("="*60)
    print("1. 특정 논문 기반 추천")
    print("="*60)
    
    # 실제 존재하는 논문 ID로 테스트 (arXiv ID 형식)
    # 첫 번째 논문 ID를 사용하거나, keywords_tfidf_results.json에서 확인
    test_paper_id = "2510.05069v1"  # 수정
    
    similar = recommender.recommend_by_paper_id(test_paper_id, top_k=3)
    if similar:
        for i, paper in enumerate(similar, 1):
            metadata = paper.metadata if hasattr(paper, 'metadata') else paper.get('metadata', {})
            score = paper.score if hasattr(paper, 'score') else paper.get('score', 0)
            print(f"\n{i}. {metadata.get('title', 'N/A')}")
            print(f"   Score: {score:.4f}")
    else:
        print(f"No similar papers found for {test_paper_id}")
    
    print("\n" + "="*60)
    print("2. 키워드 기반 추천")
    print("="*60)
    
    recommendations = recommender.recommend_by_keywords(
        keywords=["deep learning", "transformer"],
        top_k=3
    )
    for i, paper in enumerate(recommendations, 1):
        metadata = paper.metadata if hasattr(paper, 'metadata') else paper.get('metadata', {})
        score = paper.score if hasattr(paper, 'score') else paper.get('score', 0)
        print(f"\n{i}. {metadata.get('title', 'N/A')}")
        print(f"   Score: {score:.4f}")
    
    print("\n" + "="*60)
    print("3. 사용자 읽은 논문 기반 추천 (개인화)")
    print("="*60)
    
    user_recommendations = recommender.recommend_by_user_history(
        read_paper_ids=["2510.05069v1", "2510.05094v1"],
        top_k=5
    )
    for i, paper in enumerate(user_recommendations, 1):
        print(f"\n{i}. {paper['metadata']['title']}")
        print(f"   Score: {paper['score']:.4f}")
    
    print("\n" + "="*60)
    print("4. 복합 추천 (읽은 논문 + 키워드 + 하이라이트)")
    print("="*60)
    
    hybrid = recommender.hybrid_recommendation(
        read_paper_ids=["2510.05094v1"],
        keywords=["neural network", "optimization"],
        highlight_texts=[
            "attention mechanism is crucial",
            "transformer architecture"
        ],
        top_k=5
    )
    for i, paper in enumerate(hybrid, 1):
        print(f"\n{i}. {paper['metadata']['title']}")
        print(f"   Score: {paper['score']:.4f}")