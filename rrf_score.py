# ============================================================
# Mariano LegRAG IA - Reciprocal Rank Fusion _ Combinar resultados de búsqueda
# ============================================================

from typing import List, Tuple

def reciprocal_rank_fusion(
    results_lists: List[List[Tuple[str, float]]],
    k: int = 60
) -> List[Tuple[str, float]]:
    scores = {}
    
    for result_list in results_lists:
        for rank, (text, _) in enumerate(result_list):
            rrf_score = 1 / (rank + k)
            if text in scores:
                scores[text] += rrf_score
            else:
                scores[text] = rrf_score
    
    # Ordenar por puntaje RRF descendente
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [(text, score) for text, score in sorted_results]