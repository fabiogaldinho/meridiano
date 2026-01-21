# newsletter.py

import os, json, time, anthropic, importlib
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

import database
import config_base as config
from utils import logger, similaridade_cosseno, deduplicar_artigos

from run_briefing import send_telegram_notification, TELEGRAM_CHAT_ID

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY não encontrada no .env")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


NEWSLETTER_MODEL = config.NEWSLETTER_MODEL
PROMPT_NEWSLETTER = config.PROMPT_NEWSLETTER
MIN_ARTICLES_PER_FEED = 4
BATCH_POLL_INTERVAL = 30
DEFAULT_MIN_SCORE = config.DEFAULT_MIN_SCORE
DEFAULT_LIMIT = config.DEFAULT_LIMIT


def get_feed_config(feed_name: str) -> dict:
    """
    Carrega configuração de newsletter para um feed específico.
    Busca MIN_SCORE_NEWSLETTER no módulo do feed, ou usa default.
    """
    try:
        feed_module = importlib.import_module(f"feeds.{feed_name}")
        min_score = getattr(feed_module, 'MIN_SCORE_NEWSLETTER', DEFAULT_MIN_SCORE)
        limit = getattr(feed_module, 'NEWSLETTER_LIMIT', DEFAULT_LIMIT)
        return {"min_score": min_score, "limit": limit}
    except ImportError:
        logger.warning(f"Config não encontrada para feed '{feed_name}', usando defaults")
        return {"min_score": DEFAULT_MIN_SCORE, "limit": DEFAULT_LIMIT}


def coletar_artigos_para_newsletter() -> dict:
    """
    Coleta artigos elegíveis de todos os feeds ativos.
    """
    from utils import get_active_feeds
    
    artigos_por_feed = {}
    
    feeds_ativos = get_active_feeds()
    logger.info(f"Feeds ativos encontrados: {feeds_ativos}")
    
    for feed_name in feeds_ativos:
        feed_config = get_feed_config(feed_name)
        
        artigos = database.get_articles_for_newsletter(
            feed_profile=feed_name,
            min_score=feed_config["min_score"],
            days_back=3,
            limit=50
        )

        logger.info(f"  {feed_name}: {len(artigos)} artigos brutos (min_score={feed_config['min_score']})")

        # Deduplicar
        artigos, ids_removidos = deduplicar_artigos(artigos, threshold=0.85, retornar_removidos=True)

        # Marcar artigos deduplicados no banco
        if ids_removidos:
            database.mark_articles_newsletter_deduplicated(ids_removidos)

        # Aplicar limite após deduplicação
        artigos = artigos[:feed_config["limit"]]

        logger.info(f"  {feed_name}: {len(artigos)} artigos após deduplicação e limite")

        if len(artigos) >= MIN_ARTICLES_PER_FEED:
            artigos_por_feed[feed_name] = artigos
        else:
            logger.info(f"  {feed_name}: pulando (menos de {MIN_ARTICLES_PER_FEED} artigos)")
    
    return artigos_por_feed


def montar_requests_batch(artigos_por_feed: dict) -> list:
    """
    Monta lista de requests para a Anthropic Batch API.
    """
    requests = []
    
    for feed_name, artigos in artigos_por_feed.items():
        for artigo in artigos:
            custom_id = f"{feed_name}-{artigo['id']}"
            
            # Monta o prompt com o conteúdo do artigo
            prompt = PROMPT_NEWSLETTER.format(raw_content=artigo['raw_content'])
            
            request = {
                "custom_id": custom_id,
                "params": {
                    "model": NEWSLETTER_MODEL,
                    "max_tokens": 2024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            }
            
            requests.append(request)
    
    total = len(requests)
    feeds = len(artigos_por_feed)
    logger.info(f"Montadas {total} requests para {feeds} feeds")
    
    return requests


def enviar_batch_anthropic(requests_list: list, description: str = "newsletter") -> str | None:
    """
    Envia batch para Anthropic API.
    """
    if not requests_list:
        logger.warning(f"Lista de requests vazia para {description}")
        return None
    
    logger.info(f"Enviando batch '{description}' com {len(requests_list)} requests para Anthropic...")
    
    try:
        batch = client.beta.messages.batches.create(requests=requests_list)
        
        logger.info(f"Batch criado com sucesso!")
        logger.info(f"  ID: {batch.id}")
        logger.info(f"  Status: {batch.processing_status}")
        
        return batch.id
    
    except Exception as e:
        logger.error(f"Erro ao criar batch '{description}': {e}")
        return None


def aguardar_batch_anthropic(batch_id: str, description: str = "newsletter"):
    """
    Aguarda batch da Anthropic terminar de processar.
    """
    if not batch_id:
        return None
    
    logger.info(f"Aguardando batch '{description}' ({batch_id})...")
    
    start_time = time.time()
    
    while True:
        try:
            batch = client.beta.messages.batches.retrieve(batch_id)
            
            elapsed_minutes = (time.time() - start_time) / 60
            
            logger.info(f"  Status: {batch.processing_status} | Tempo: {elapsed_minutes:.1f}min")
            
            if batch.processing_status == "ended":
                logger.info(f"Batch '{description}' concluído em {elapsed_minutes:.1f} minutos")
                return batch
            
            elif batch.processing_status in ("canceled", "canceling"):
                logger.error(f"Batch '{description}' foi cancelado")
                return None
            
            time.sleep(BATCH_POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do batch: {e}")
            time.sleep(BATCH_POLL_INTERVAL)


def processar_resultados_batch(batch_id: str, description: str = "newsletter") -> dict | None:
    """
    Baixa e processa resultados de um batch concluído.
    """
    if not batch_id:
        return None
    
    logger.info(f"Processando resultados do batch '{description}'...")
    
    try:
        resultados = {}
        erros = 0
        
        for result in client.beta.messages.batches.results(batch_id):
            custom_id = result.custom_id
            
            if result.result.type == "succeeded":
                # Extrai o texto da resposta
                texto = result.result.message.content[0].text
                resultados[custom_id] = texto.strip()
            else:
                # Erro nessa request específica
                logger.warning(f"  Erro em {custom_id}: {result.result.type}")
                erros += 1
        
        logger.info(f"Resultados processados: {len(resultados)} sucesso, {erros} erros")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro ao processar resultados do batch: {e}")
        return None


def montar_newsletter_markdown(
    resultados_batch: dict,
    artigos: list,
    feed_name: str
) -> tuple[str, str | None, list[int]]:
    """
    Monta o markdown final da newsletter para um feed.
    """
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    linhas = []
    
    # Encontrar featured_image (primeiro artigo com imagem)
    featured_image = None
    for artigo in artigos:
        if artigo.get('image_url'):
            featured_image = artigo['image_url']
            break
    
    # IDs dos artigos incluídos
    article_ids = []
    
    # Montar cada item
    itens_adicionados = 0
    for artigo in artigos:
        custom_id = f"{feed_name}-{artigo['id']}"
        
        # Verifica se existe resultado para esse artigo
        if custom_id not in resultados_batch:
            logger.warning(f"  Sem resultado para {custom_id}, pulando...")
            continue
        
        texto_gerado = resultados_batch[custom_id]
        
        # Link interno para a página do artigo
        link_fonte = f"https://galdinho.news/articles/{artigo['id']}"
        
        nome_fonte = artigo.get('feed_source', 'Fonte')
        
        # Adiciona o item
        linhas.append(texto_gerado)
        linhas.append(f"Fonte: [{nome_fonte}]({link_fonte})")
        linhas.append("")
        linhas.append("---")
        linhas.append("")
        
        article_ids.append(artigo['id'])
        itens_adicionados += 1
    
    # Remove último separador
    if linhas[-2] == "---":
        linhas = linhas[:-2]
    
    markdown = "\n".join(linhas)
    
    logger.info(f"Newsletter {feed_name}: {itens_adicionados} itens montados")
    
    return markdown, featured_image, article_ids



def executar_pipeline_newsletter(feed_name: str = None) -> dict:
    """
    Executa o pipeline completo de geração de newsletter.
    
    Se feed_name for especificado, gera apenas para esse feed.
    Se None, gera para todos os feeds ativos com artigos suficientes.
    """
    logger.info(f"{'='*60}")
    logger.info(f"PIPELINE NEWSLETTER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info(f"{'='*60}")
    
    # 1. Coletar artigos
    logger.info("\n>>> FASE 1: Coleta de artigos <<<")
    artigos_por_feed = coletar_artigos_para_newsletter()
    
    # Filtrar por feed específico se solicitado
    if feed_name:
        if feed_name in artigos_por_feed:
            artigos_por_feed = {feed_name: artigos_por_feed[feed_name]}
        else:
            logger.warning(f"Feed '{feed_name}' não tem artigos suficientes")
            return {"status": "sem_artigos", "feed": feed_name}
    
    if not artigos_por_feed:
        logger.info("Nenhum feed com artigos suficientes para newsletter")
        return {"status": "sem_artigos", "feeds_processados": 0}
    
    # 2. Montar requests do batch
    logger.info("\n>>> FASE 2: Montagem de requests <<<")
    requests_list = montar_requests_batch(artigos_por_feed)
    
    if not requests_list:
        logger.warning("Nenhum request montado")
        return {"status": "erro", "fase": "montagem_requests"}
    
    # 3. Enviar batch
    logger.info("\n>>> FASE 3: Envio do batch <<<")
    batch_id = enviar_batch_anthropic(requests_list)
    
    if not batch_id:
        logger.error("Falha ao enviar batch")
        return {"status": "erro", "fase": "envio_batch"}
    
    # 4. Aguardar processamento
    logger.info("\n>>> FASE 4: Aguardando processamento <<<")
    batch_completo = aguardar_batch_anthropic(batch_id)
    
    if not batch_completo:
        logger.error("Batch não completou com sucesso")
        return {"status": "erro", "fase": "processamento_batch", "batch_id": batch_id}
    
    # 5. Processar resultados
    logger.info("\n>>> FASE 5: Processamento de resultados <<<")
    resultados = processar_resultados_batch(batch_id)
    
    if not resultados:
        logger.error("Falha ao processar resultados")
        return {"status": "erro", "fase": "processamento_resultados", "batch_id": batch_id}
    
    # 6. Montar e salvar newsletter de cada feed
    logger.info("\n>>> FASE 6: Montagem e salvamento <<<")
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
            "artigos": len(article_ids),
            "featured_image": featured_image is not None
        })
        
        logger.info(f"  ✓ Newsletter {feed} salva (ID: {newsletter_id}, {len(article_ids)} artigos)")

        # Enviar notificação Telegram
        feed_config = get_feed_config(feed)
        try:
            feed_module = importlib.import_module(f"feeds.{feed}")
            chat_ids = getattr(feed_module, 'TELEGRAM_CHAT_ID', {TELEGRAM_CHAT_ID: f"https://galdinho.news/newsletters/{newsletter_id}"})
        except ImportError:
            chat_ids = {TELEGRAM_CHAT_ID: f"https://galdinho.news/newsletters/{newsletter_id}"}
        
        for chatid, chaturl in chat_ids.items():
            notification_message = f"""
            <b>📰 Nova Newsletter Disponível</b>

            <b>Feed:</b> {feed}
            Acesse em: https://galdinho.news/newsletters/{newsletter_id}
            
            """
            send_telegram_notification(chatid, notification_message)
            logger.info(f"  📨 Notificação enviada para chat {chatid}")

    
    # Resumo final
    logger.info(f"\n{'='*60}")
    logger.info(f"PIPELINE CONCLUÍDO")
    logger.info(f"{'='*60}")
    
    return {
        "status": "sucesso",
        "batch_id": batch_id,
        "total_requests": len(requests_list),
        "total_resultados": len(resultados),
        "newsletters": newsletters_salvas
    }