import sys

# Batch ID a recuperar
BATCH_ID = "msgbatch_01SS4hM6tkEjiiZecWfrksau"

try:
    import database
    from newsletter import (
        coletar_artigos_para_newsletter,
        processar_resultados_batch,
        montar_newsletter_markdown,
        logger
    )
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)


def main():
    logger.info(f"{'='*60}")
    logger.info(f"RECUPERANDO BATCH NEWSLETTER: {BATCH_ID}")
    logger.info(f"{'='*60}")
    
    # Inicializar banco
    database.init_db()
    
    # 1. Recolher artigos (mesma lógica do pipeline original)
    logger.info("\n>>> Recoletando artigos <<<")
    artigos_por_feed = coletar_artigos_para_newsletter()
    
    if not artigos_por_feed:
        logger.error("Nenhum artigo encontrado!")
        sys.exit(1)
    
    # 2. Baixar resultados do batch já processado
    logger.info(f"\n>>> Baixando resultados do batch <<<")
    resultados = processar_resultados_batch(BATCH_ID, description="newsletter (recuperado)")
    
    if not resultados:
        logger.error("Falha ao baixar resultados!")
        sys.exit(1)
    
    logger.info(f"Resultados recuperados: {len(resultados)}")
    
    # 3. Montar e salvar newsletters
    logger.info("\n>>> Montagem e salvamento <<<")
    newsletters_salvas = []
    
    for feed, artigos in artigos_por_feed.items():
        logger.info(f"\nProcessando feed: {feed}")
        
        markdown, featured_image, article_ids = montar_newsletter_markdown(
            resultados_batch=resultados,
            artigos=artigos,
            feed_name=feed
        )
        
        if not article_ids:
            logger.warning(f"  Nenhum artigo incluído para {feed}, pulando...")
            continue
        
        # Salvar no banco
        newsletter_id = database.save_newsletter(
            newsletter_markdown=markdown,
            contributing_article_ids=article_ids,
            feed_profile=feed,
            featured_image=featured_image
        )
        
        newsletters_salvas.append({
            "feed": feed,
            "newsletter_id": newsletter_id,
            "artigos": len(article_ids)
        })
        
        logger.info(f"  ✓ Newsletter {feed} salva (ID: {newsletter_id}, {len(article_ids)} artigos)")
    
    # Resumo
    logger.info(f"\n{'='*60}")
    logger.info(f"RECUPERAÇÃO CONCLUÍDA!")
    logger.info(f"{'='*60}")
    for nl in newsletters_salvas:
        logger.info(f"  {nl['feed']}: ID {nl['newsletter_id']} ({nl['artigos']} artigos)")


if __name__ == "__main__":
    main()