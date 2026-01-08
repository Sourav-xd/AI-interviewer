#memory_service.py
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class MemoryService:

    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384
        self.index = faiss.IndexFlatL2(self.embedding_dim)

        #metadata store aligned with the faiss index
        self.metadata: List[Dict[str, Any]] = []


    # embed text
    def _embed(self, text: str) -> np.ndarray:
        embedding = self.embedder.encode(text)
        
        return np.array([embedding]).astype("float32")
    
    #store interaction
    def store_interaction(
            self,
            question: str,
            answer: str,
            evaluation: Dict[str, Any],
            topic: str,
            interview_round: int
    ):
        
        summary_text = f"""
        Question: {question}
        Answer: {answer}
        Correctness: {evaluation.get("correctness_score")}
        Depth: {evaluation.get("depth_level")}
        """

        vector = self._embed(summary_text)

        self.index.add(vector)
        self.metadata.append(
            {
                "question": question,
                "answer": answer,
                "topic": topic,
                "correctness_score": evaluation.get("correctness_score"),
                "depth_level": evaluation.get("depth_level"),
                "round": interview_round
            }
        )

    
    # retrieve relevant context
    def get_relevant_context(
            self,
            query: str,
            top_k: int = 3
    )-> List[Dict[str, Any]]:
        
        if self.index.ntotal == 0:
            return []
        
        query_vector = self._embed(query)
        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for idx in indices[0]:
            if idx<len(self.metadata):
                results.append(self.metadata[idx])

        return results
    

    # weak topic detection
    def get_weak_topics(self)-> List[str]:

        topic_scores = {}
        for item in self.metadata:
            topic = item["topic"]
            score = item["correctness_score"]

            if topic not in topic_scores:
                topic_scores[topic] = []

            topic_scores[topic].append(score)

        weak_topics = []
        for topic, scores in topic_scores.items():
            avg_score = sum(scores)/len(scores)
            if avg_score < 0.4:
                weak_topics.append(topic)
        
        return weak_topics
    

    #candidate profile summary
    def summarize_candidate_profile(self)-> Dict[str, Any]:

        strengths = []
        weaknesses = []

        topic_scores = {}

        for item in self.metadata:
            topic = item["topic"]
            score = item["correctness_score"]

            topic_scores.setdefault(topic, []).append(score)

        for topic, scores in topic_scores.items():
            avg = sum(scores)/len(scores)
            if avg >= 0.5:
                strengths.append(topic)
            else:
                weaknesses.append(topic)

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "total_interactions": len(self.metadata)
        }
    

# Singleton instance (process-level memory)
#memory_service = MemoryService()
