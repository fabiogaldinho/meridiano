#!/usr/bin/env python3
"""
Script para recuperar um batch existente e continuar o pipeline.

Uso:
    python recuperar_batch.py

Ou no Docker:
    docker cp recuperar_batch.py meridiano:/app/
    docker exec -it meridiano python recuperar_batch.py
"""

import re
import sys

# Configuração do batch a recuperar
BATCH_ID = "batch_696a65ccbc3c8190a993f21dca491555"

# Imports do projeto
try:
    from batch import (
        batch_client,
        aguardar_batch,
        baixar_resultados_batch,
        fetch_approved_content,
        batch_summary,
        batch_embedding,
        batch_rating
    )
    from database import update_article_filter_score
    from utils import logger
    import database
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de rodar este script dentro do container meridiano")
    sys.exit(1)


def processar_resultados_filtro(resultados):
    """
    Processa os resultados do batch de filtro e atualiza o banco.
    Replica a lógica do batch_filter (linhas 403-443 do batch.py).
    """
    stats = {"total": len(resultados), "aprovados": 0, "rejeitados": 0, "erros": 0}
    
    for custom_id, resposta in resultados.items():
        # Extrair article_id do custom_id (formato: "feed-123")
        parts = custom_id.rsplit("-", 1)
        if len(parts) != 2:
            logger.warning(f"custom_id inválido: {custom_id}")
            stats["erros"] += 1
            continue
        
        try:
            article_id = int(parts[1])
        except ValueError:
            logger.warning(f"Não foi possível extrair article_id de: {custom_id}")
            stats["erros"] += 1
            continue
        
        # Parsear score da resposta (1-5)
        match = re.search(r'\b([1-5])\b', resposta.strip())
        if match:
            score = int(match.group(1))
        else:
            logger.warning(f"Score inválido para {custom_id}: '{resposta}'")
            score = 3  # Default se não conseguir parsear
        
        # Atualizar no banco
        update_article_filter_score(article_id, score)
        
        if score >= 3:
            stats["aprovados"] += 1
        else:
            stats["rejeitados"] += 1
    
    return stats


def main():
    logger.info(f"{'='*60}")
    logger.info(f"RECUPERANDO BATCH: {BATCH_ID}")
    logger.info(f"{'='*60}")
    
    # Inicializar banco
    database.init_db()
    
    # 1. Aguardar batch completar
    logger.info(f"\n>>> Aguardando batch completar <<<")
    batch_status = aguardar_batch(BATCH_ID, description="filter (recuperado)")
    
    #if not batch_status:
        logger.error("Batch falhou ou timeout!")
        sys.exit(1)
    
    # 2. Baixar resultados
    logger.info(f"\n>>> Baixando resultados <<<")
    resultados = baixar_resultados_batch(batch_status, description="filter")
    
    #if not resultados:
        logger.error("Falha ao baixar resultados!")
        sys.exit(1)
    
    logger.info(f"Resultados baixados: {len(resultados)} respostas")
    
    # 3. Processar resultados (atualizar banco com scores)
    logger.info(f"\n>>> Processando resultados do filtro <<<")
    stats_filter = processar_resultados_filtro(resultados)
    logger.info(f"Filtro concluído: {stats_filter}")
    
    # 4. Continuar pipeline - Fase 3
    logger.info(f"\n>>> FASE 3: Busca de conteúdo <<<")
    stats_content = fetch_approved_content(feed_profile=None)
    logger.info(f"Fase 3 concluída: {stats_content}")
    
    # 5. Continuar pipeline - Fase 4a
    logger.info(f"\n>>> FASE 4a: Sumarização batch <<<")
    stats_summary = batch_summary(feed_profile=None)
    logger.info(f"Fase 4a concluída: {stats_summary}")
    
    # 6. Continuar pipeline - Fase 4b
    logger.info(f"\n>>> FASE 4b: Embeddings batch <<<")
    stats_embedding = batch_embedding(feed_profile=None)
    logger.info(f"Fase 4b concluída: {stats_embedding}")
    
    # 7. Continuar pipeline - Fase 5
    logger.info(f"\n>>> FASE 5: Rating batch <<<")
    stats_rating = batch_rating(feed_profile=None)
    logger.info(f"Fase 5 concluída: {stats_rating}")
    
    # Resumo final
    logger.info(f"\n{'='*60}")
    logger.info(f"PIPELINE CONCLUÍDO!")
    logger.info(f"{'='*60}")
    logger.info(f"Filtro:    {stats_filter}")
    logger.info(f"Conteúdo:  {stats_content}")
    logger.info(f"Sumário:   {stats_summary}")
    logger.info(f"Embedding: {stats_embedding}")
    logger.info(f"Rating:    {stats_rating}")


if __name__ == "__main__":
    main()
