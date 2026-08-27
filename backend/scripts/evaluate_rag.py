"""
RAG Evaluation Script for AyurPedia Hackathon
Tests retrieval quality, generation quality, and system performance
"""

import sys
import os
import time
import logging
from typing import Dict, List, Any
from pathlib import Path
import statistics

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Comprehensive RAG system evaluator."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.results = {
            "retrieval_metrics": {},
            "generation_metrics": {},
            "performance_metrics": {},
            "overall_score": 0.0
        }
    
    def evaluate_retrieval_quality(self, retriever, test_queries: List[Dict]) -> Dict[str, float]:
        """Evaluate retrieval quality with ground truth queries.
        
        Args:
            retriever: Retriever instance
            test_queries: List of {query, expected_docs, expected_keywords} test cases
            
        Returns:
            Dictionary of retrieval metrics
        """
        logger.info("Evaluating retrieval quality...")
        
        precision_scores = []
        recall_scores = []
        mrr_scores = []
        ndcg_scores = []
        
        for test_case in test_queries:
            query = test_case["query"]
            expected_sources = set(test_case["expected_docs"])
            expected_keywords = set(test_case.get("expected_keywords", []))
            
            # Retrieve documents
            retrieved_docs = retriever.search(query, jurisdiction="India")
            retrieved_sources = set()
            retrieved_texts = []
            
            for doc in retrieved_docs:
                source = doc.metadata.get("source", "")
                retrieved_sources.add(source)
                retrieved_texts.append(doc.text.lower())
            
            # Calculate traditional metrics
            if retrieved_sources:
                precision = len(retrieved_sources & expected_sources) / len(retrieved_sources)
                recall = len(retrieved_sources & expected_sources) / len(expected_sources) if expected_sources else 0
                
                # MRR: reciprocal rank of first relevant document
                mrr = 0.0
                for i, doc in enumerate(retrieved_docs):
                    if doc.metadata.get("source") in expected_sources:
                        mrr = 1.0 / (i + 1)
                        break
                
                # NDCG: Normalized Discounted Cumulative Gain
                ndcg = self._calculate_ndcg(retrieved_docs, expected_sources, expected_keywords)
                
                precision_scores.append(precision)
                recall_scores.append(recall)
                mrr_scores.append(mrr)
                ndcg_scores.append(ndcg)
        
        metrics = {
            "precision_at_k": statistics.mean(precision_scores) if precision_scores else 0.0,
            "recall_at_k": statistics.mean(recall_scores) if recall_scores else 0.0,
            "mrr": statistics.mean(mrr_scores) if mrr_scores else 0.0,
            "ndcg": statistics.mean(ndcg_scores) if ndcg_scores else 0.0,
            "num_queries": len(test_queries)
        }
        
        self.results["retrieval_metrics"] = metrics
        logger.info(f"Retrieval metrics: {metrics}")
        return metrics
    
    def _calculate_ndcg(self, retrieved_docs: List, expected_sources: set, expected_keywords: set) -> float:
        """Calculate Normalized Discounted Cumulative Gain.
        
        Args:
            retrieved_docs: List of retrieved documents
            expected_sources: Set of expected source names
            expected_keywords: Set of expected keywords
            
        Returns:
            NDCG score
        """
        dcg = 0.0
        for i, doc in enumerate(retrieved_docs):
            relevance = 0
            # Check source match
            if doc.metadata.get("source") in expected_sources:
                relevance = 2
            # Check keyword match
            elif expected_keywords:
                doc_text = doc.text.lower()
                if any(keyword in doc_text for keyword in expected_keywords):
                    relevance = 1
            
            # DCG formula: relevance / log2(i+2)
            dcg += relevance / (i + 2) if i > 0 else relevance
        
        # Ideal DCG (all relevant docs at top)
        ideal_relevances = sorted([2] * len(expected_sources) + [1] * len(expected_keywords), reverse=True)
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances[:len(retrieved_docs)]):
            idcg += relevance / (i + 2) if i > 0 else relevance
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def evaluate_generation_quality(self, agentic_rag, test_queries: List[Dict]) -> Dict[str, float]:
        """Evaluate generation quality with LLM-as-a-judge.
        
        Args:
            agentic_rag: AgenticRAGWorkflow instance
            test_queries: List of test queries
            
        Returns:
            Dictionary of generation metrics
        """
        logger.info("Evaluating generation quality...")
        
        relevance_scores = []
        faithfulness_scores = []
        citation_accuracy_scores = []
        latencies = []
        
        for test_case in test_queries:
            query = test_case["query"]
            
            # Generate response
            start_time = time.time()
            response = agentic_rag.invoke(query, jurisdiction="India", language="en")
            latency = time.time() - start_time
            latencies.append(latency)
            
            # Score response (simplified - in production use LLM-as-a-judge)
            relevance_score = self._score_relevance(response["response"], query)
            faithfulness_score = self._score_faithfulness(response, query)
            citation_score = self._score_citations(response["citations"])
            
            relevance_scores.append(relevance_score)
            faithfulness_scores.append(faithfulness_score)
            citation_accuracy_scores.append(citation_score)
        
        metrics = {
            "relevance": statistics.mean(relevance_scores) if relevance_scores else 0.0,
            "faithfulness": statistics.mean(faithfulness_scores) if faithfulness_scores else 0.0,
            "citation_accuracy": statistics.mean(citation_accuracy_scores) if citation_accuracy_scores else 0.0,
            "avg_latency": statistics.mean(latencies) if latencies else 0.0,
            "num_queries": len(test_queries)
        }
        
        self.results["generation_metrics"] = metrics
        logger.info(f"Generation metrics: {metrics}")
        return metrics
    
    def evaluate_performance(self, agentic_rag, test_queries: List[str]) -> Dict[str, float]:
        """Evaluate system performance metrics.
        
        Args:
            agentic_rag: AgenticRAGWorkflow instance
            test_queries: List of test queries
            
        Returns:
            Dictionary of performance metrics
        """
        logger.info("Evaluating system performance...")
        
        latencies = []
        success_count = 0
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = agentic_rag.invoke(query, jurisdiction="India", language="en")
                latency = time.time() - start_time
                
                latencies.append(latency)
                if response.get("response"):
                    success_count += 1
            except Exception as e:
                logger.error(f"Query failed: {query}, error: {e}")
        
        metrics = {
            "avg_latency": statistics.mean(latencies) if latencies else 0.0,
            "p50_latency": statistics.median(latencies) if latencies else 0.0,
            "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0,
            "success_rate": success_count / len(test_queries) if test_queries else 0.0,
            "total_queries": len(test_queries)
        }
        
        self.results["performance_metrics"] = metrics
        logger.info(f"Performance metrics: {metrics}")
        return metrics
    
    def _score_relevance(self, response: str, query: str) -> float:
        """Score response relevance (simplified heuristic)."""
        if not response:
            return 0.0
        
        # Check if response contains key terms from query
        query_terms = set(query.lower().split())
        response_terms = set(response.lower().split())
        
        overlap = len(query_terms & response_terms) / len(query_terms) if query_terms else 0.0
        return min(overlap * 2, 1.0)  # Scale to 0-1
    
    def _score_faithfulness(self, response: Dict, query: str) -> float:
        """Score response faithfulness to retrieved context."""
        vector_context = response.get("vector_context", [])
        citations = response.get("citations", [])
        
        if not vector_context:
            return 0.5  # Neutral score if no context
        
        # Check if citations match retrieved sources
        retrieved_sources = set()
        for ctx in vector_context:
            retrieved_sources.add(ctx["metadata"].get("source", "").lower())
        
        citation_sources = set()
        for citation in citations:
            citation_sources.add(citation.get("source", "").lower())
        
        if not citation_sources:
            return 0.3  # Low score if no citations despite context
        
        overlap = len(retrieved_sources & citation_sources) / len(citation_sources)
        return overlap
    
    def _score_citations(self, citations: List[Dict]) -> float:
        """Score citation quality."""
        if not citations:
            return 0.0
        
        # Check citation format
        valid_citations = 0
        for citation in citations:
            if citation.get("source") and citation.get("text"):
                valid_citations += 1
        
        return valid_citations / len(citations)
    
    def calculate_overall_score(self) -> float:
        """Calculate overall RAG quality score."""
        retrieval_score = (
            self.results["retrieval_metrics"].get("precision_at_k", 0.0) * 0.4 +
            self.results["retrieval_metrics"].get("recall_at_k", 0.0) * 0.3 +
            self.results["retrieval_metrics"].get("mrr", 0.0) * 0.3
        )
        
        generation_score = (
            self.results["generation_metrics"].get("relevance", 0.0) * 0.4 +
            self.results["generation_metrics"].get("faithfulness", 0.0) * 0.3 +
            self.results["generation_metrics"].get("citation_accuracy", 0.0) * 0.3
        )
        
        performance_score = min(
            self.results["performance_metrics"].get("success_rate", 0.0),
            1.0 - (self.results["performance_metrics"].get("avg_latency", 10.0) / 20.0)  # Penalize high latency
        )
        
        overall = retrieval_score * 0.4 + generation_score * 0.4 + performance_score * 0.2
        self.results["overall_score"] = overall
        return overall


def main():
    """Run comprehensive RAG evaluation."""
    logger.info("Starting RAG evaluation for AyurPedia...")
    
    # Initialize components (mock for demonstration)
    from app.rag.retriever import Retriever
    from app.rag.hybrid_retriever import HybridRetriever
    from app.core.database import QdrantDB
    from app.core.config import get_config
    from app.graph.agents import get_agentic_rag
    from app.core.llm import get_llm_client
    
    try:
        config = get_config()
        
        # Initialize LLM client first
        llm_client = get_llm_client()
        logger.info("LLM client initialized")
        
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        
        # Use HybridRetriever with Cohere rerank for better precision/recall
        retriever = HybridRetriever(qdrant_db, top_k=config.top_k_results, use_rerank=True)
        logger.info("Using HybridRetriever with Cohere rerank")
        
        agentic_rag = get_agentic_rag(retriever)
        
        # Define test queries with enhanced ground truth
        retrieval_test_cases = [
            {
                "query": "What are the restrictions under Section 3(p) for Ayurvedic formulations?",
                "expected_docs": ["Patents Act 1970"],
                "expected_keywords": ["section 3(p)", "traditional knowledge", "patentability", "novelty", "prior art"]
            },
            {
                "query": "FSSAI Ayurveda-Aahar regulatory requirements",
                "expected_docs": ["FSSAI Ayurveda-Aahar Regulations 2022"],
                "expected_keywords": ["fssai", "ayurveda aahar", "schedule a", "food safety", "nutraceutical"]
            },
            {
                "query": "WIPO GRATK treaty traditional knowledge protection",
                "expected_docs": ["WIPO GRATK Treaty 2024"],
                "expected_keywords": ["wipo", "gratk", "genetic resources", "traditional knowledge", "international treaty"]
            },
            {
                "query": "Biological Diversity Act NBA approval process",
                "expected_docs": ["Biological Diversity Act 2002"],
                "expected_keywords": ["biological diversity", "nba", "benefit sharing", "access", "national biodiversity authority"]
            },
            {
                "query": "TRIPS Agreement intellectual property provisions",
                "expected_docs": ["TRIPS Agreement"],
                "expected_keywords": ["trips", "intellectual property", "trade-related", "patent", "copyright"]
            }
        ]
        
        generation_test_cases = [
            {"query": "Explain Section 3(p) of the Patents Act 1970"},
            {"query": "What is the process for NBA approval for Ayurvedic formulations?"},
            {"query": "Compare Indian and international traditional knowledge protection"},
            {"query": "Classify a herbal formulation with ashwagandha and turmeric"}
        ]
        
        performance_test_queries = [
            "What is Section 3(p)?",
            "Explain prior art requirements",
            "FSSAI Ayurveda-Aahar classification",
            "WIPO GRATK provisions",
            "NBA approval process"
        ]
        
        # Run evaluation
        evaluator = RAGEvaluator()
        
        print("\n" + "="*60)
        print("RAG EVALUATION FOR AYURPEDIA")
        print("="*60 + "\n")
        
        # Retrieval quality
        print("1. Evaluating Retrieval Quality...")
        evaluator.evaluate_retrieval_quality(retriever, retrieval_test_cases)
        
        # Generation quality
        print("\n2. Evaluating Generation Quality...")
        evaluator.evaluate_generation_quality(agentic_rag, generation_test_cases)
        
        # Performance
        print("\n3. Evaluating System Performance...")
        evaluator.evaluate_performance(agentic_rag, performance_test_queries)
        
        # Overall score
        print("\n4. Calculating Overall Score...")
        overall_score = evaluator.calculate_overall_score()
        
        # Display results
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        print(f"\nRetrieval Metrics:")
        print(f"  Precision@K: {evaluator.results['retrieval_metrics'].get('precision_at_k', 0):.3f}")
        print(f"  Recall@K: {evaluator.results['retrieval_metrics'].get('recall_at_k', 0):.3f}")
        print(f"  MRR: {evaluator.results['retrieval_metrics'].get('mrr', 0):.3f}")
        
        print(f"\nGeneration Metrics:")
        print(f"  Relevance: {evaluator.results['generation_metrics'].get('relevance', 0):.3f}")
        print(f"  Faithfulness: {evaluator.results['generation_metrics'].get('faithfulness', 0):.3f}")
        print(f"  Citation Accuracy: {evaluator.results['generation_metrics'].get('citation_accuracy', 0):.3f}")
        
        print(f"\nPerformance Metrics:")
        print(f"  Avg Latency: {evaluator.results['performance_metrics'].get('avg_latency', 0):.3f}s")
        print(f"  P50 Latency: {evaluator.results['performance_metrics'].get('p50_latency', 0):.3f}s")
        print(f"  P95 Latency: {evaluator.results['performance_metrics'].get('p95_latency', 0):.3f}s")
        print(f"  Success Rate: {evaluator.results['performance_metrics'].get('success_rate', 0):.3f}")
        
        print(f"\nOVERALL RAG SCORE: {overall_score:.3f}/1.0")
        print("="*60 + "\n")
        
        return evaluator.results
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise


if __name__ == "__main__":
    main()