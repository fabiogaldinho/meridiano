# newsletter.py

import os, json, time, anthropic, importlib
from datetime import datetime
from dotenv import load_dotenv

import database
import config_base as config
from utils import logger

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
            limit=feed_config["limit"]
        )
        
        logger.info(f"  {feed_name}: {len(artigos)} artigos (min_score={feed_config['min_score']})")
        
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