import json, time, tempfile, openai
from pathlib import Path
from datetime import datetime

import config_base as config
from utils import get_active_feeds, logger


# Cliente OpenAI
batch_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

# Intervalo entre verificações de status (em segundos)
BATCH_POLL_INTERVAL = 60

# Timeout máximo para aguardar batch (em segundos) - 6 horas
#BATCH_TIMEOUT = 6 * 60 * 60



def enviar_batch(requests_list, description="batch", endpoint="/v1/chat/completions"):
    """
    Cria arquivo JSONL e envia para a Batch API da OpenAI.
    """
    if not requests_list:
        logger.warning(f"Lista de requests vazia para {description}")
        return None
    
    logger.info(f"Montando batch '{description}' com {len(requests_list)} requests...")
    
    # Monta as linhas JSONL
    jsonl_lines = []
    for req in requests_list:
        if "body" in req:
            body = req["body"]
        else:
            body = {
                "model": req["model"],
                "max_completion_tokens": req.get("max_completion_tokens", 100),
                "messages": req["messages"]
            }
        
        line = {
            "custom_id": req["custom_id"],
            "method": "POST",
            "url": endpoint,
            "body": body
        }
        jsonl_lines.append(json.dumps(line))
    
    jsonl_content = "\n".join(jsonl_lines)
    
    # Cria arquivo temporário e faz upload
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(jsonl_content)
            temp_path = f.name
        
        logger.info(f"Fazendo upload do arquivo batch...")
        
        with open(temp_path, 'rb') as f:
            batch_file = batch_client.files.create(
                file=f,
                purpose="batch"
            )
        
        # Remove arquivo temporário
        Path(temp_path).unlink()
        
        logger.info(f"Arquivo enviado: {batch_file.id}")
        
        # Cria o batch
        batch = batch_client.batches.create(
            input_file_id=batch_file.id,
            endpoint=endpoint,
            completion_window="24h"
        )
        
        logger.info(f"Batch criado: {batch.id}")
        return batch.id
        
    except Exception as e:
        logger.error(f"Erro ao enviar batch: {e}")
        return None


def aguardar_batch(batch_id, description="batch"):
    """
    Aguarda um batch terminar de processar.
    """
    if not batch_id:
        return None
    
    logger.info(f"Aguardando batch '{description}' ({batch_id})...")
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        #if elapsed > BATCH_TIMEOUT:
        #    logger.error(f"Timeout aguardando batch {batch_id} ({elapsed/3600:.1f}h)")
        #    return None
        
        try:
            status = batch_client.batches.retrieve(batch_id)
            
            completed = status.request_counts.completed
            failed = status.request_counts.failed
            total = status.request_counts.total
            
            logger.info(f"  Status: {status.status} | Progresso: {completed}/{total} | Falhas: {failed}")
            
            if status.status == "completed":
                logger.info(f"Batch '{description}' concluído em {elapsed/60:.1f} minutos")
                return status
            
            elif status.status in ("failed", "expired", "cancelled"):
                logger.error(f"Batch '{description}' falhou com status: {status.status}")
                if hasattr(status, 'errors') and status.errors:
                    logger.error(f"  Erros: {status.errors}")
                return None
            
            # Ainda processando, aguarda
            time.sleep(BATCH_POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do batch: {e}")
            time.sleep(BATCH_POLL_INTERVAL)


def baixar_resultados_batch(batch_status, description="batch", is_embedding=False):
    """
    Baixa e parseia os resultados de um batch completo.
    """
    if not batch_status:
        return None
    
    output_file_id = batch_status.output_file_id
    
    if not output_file_id:
        logger.error(f"Batch '{description}' não tem output_file_id")
        return None
    
    try:
        logger.info(f"Baixando resultados do batch '{description}'...")
        
        result_content = batch_client.files.content(output_file_id)
        
        resultados = {}
        erros = 0
        
        for line in result_content.text.strip().split("\n"):
            if not line:
                continue
                
            result = json.loads(line)
            custom_id = result.get("custom_id")
            
            # Verifica se teve erro nessa request específica
            if result.get("error"):
                logger.warning(f"  Erro em {custom_id}: {result['error']}")
                erros += 1
                continue
            
            # Extrai o conteúdo da resposta
            try:
                response_body = result["response"]["body"]
                
                if is_embedding:
                    # Formato embeddings: {"data": [{"embedding": [...]}]}
                    embedding = response_body["data"][0]["embedding"]
                    resultados[custom_id] = embedding  # Lista de floats
                else:
                    # Formato chat: {"choices": [{"message": {"content": "..."}}]}
                    content = response_body["choices"][0]["message"]["content"]
                    resultados[custom_id] = content.strip()
                    
            except (KeyError, IndexError) as e:
                logger.warning(f"  Resposta malformada em {custom_id}: {e}")
                erros += 1
        
        logger.info(f"Resultados processados: {len(resultados)} ok, {erros} erros")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro ao baixar resultados do batch: {e}")
        return None


def executar_batch(requests_list, description="batch", endpoint="/v1/chat/completions", is_embedding=False):
    """
    Executa o fluxo completo: enviar → aguardar → baixar resultados.
    """
    if not requests_list:
        logger.info(f"Nada para processar em '{description}'")
        return {}
    
    # 1. Envia
    batch_id = enviar_batch(requests_list, description, endpoint)
    if not batch_id:
        return None
    
    # 2. Aguarda
    batch_status = aguardar_batch(batch_id, description)
    if not batch_status:
        return None
    
    # 3. Baixa resultados
    resultados = baixar_resultados_batch(batch_status, description, is_embedding)
    return resultados


def scrape_metadata_only(feed_profile, rss_feeds, effective_config):
    """
    Fase 1 do pipeline batch: coleta metadados do RSS sem chamar API de filtro.
    
    Salva apenas: url, title, rss_description, published_date, feed_source, url_encoding
    Deixa initial_filter_score=NULL para processamento posterior em batch.
    """
    logger.info(f"--- [BATCH] Coletando metadados RSS [{feed_profile}] ---")
    
    # Importações necessárias
    import feedparser
    from datetime import datetime, timedelta
    from models import Article
    from db import get_db_connection
    from sqlmodel import select, func
    
    # Verificar cold start
    with get_db_connection() as session:
        existing_count = session.exec(
            select(func.count(Article.id)).where(Article.feed_profile == feed_profile)
        ).one()
    
    is_cold_start = (existing_count == 0)
    
    if is_cold_start:
        max_age_days = getattr(effective_config, 'SCRAPING_MAX_AGE_DAYS_INITIAL', 7)
        logger.info(f"Cold start para '{feed_profile}' - aceitando até {max_age_days} dias")
    else:
        max_age_days = getattr(effective_config, 'SCRAPING_MAX_AGE_DAYS_NORMAL', 3)
        logger.info(f"Execução normal para '{feed_profile}' - aceitando até {max_age_days} dias")
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    new_articles_count = 0
    skipped_existing = 0
    
    if not rss_feeds:
        logger.warning(f"Nenhum RSS_FEEDS definido para '{feed_profile}'")
        return 0
    
    for feed_url in rss_feeds:
        logger.info(f"Lendo feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            logger.warning(f"Problema no feed {feed_url}: {feed.bozo_exception}")
        
        for entry in feed.entries:
            url = entry.get('link')
            if not url:
                continue
            
            # Dados básicos
            title = entry.get('title', 'No Title')
            description = entry.get('description', '') or entry.get('summary', '')
            published_parsed = entry.get('published_parsed')
            published_date = datetime(*published_parsed[:6]) if published_parsed else datetime.now()
            feed_source = feed.feed.get('title', feed_url)
            
            # URL encoding para Marreta
            url_encoding = url
            for old, new in [("/", "%2F"), (":", "%3A"), (" ", "%20"), 
                            ("?", "%3F"), ("&", "%26"), ("=", "%3D"), ("#", "%23")]:
                url_encoding = url_encoding.replace(old, new)
            url_encoding = "https://marreta.galdinho.news/p/" + url_encoding
            
            # Verificar idade
            if published_date < cutoff_date:
                continue
            
            # Verificar se já existe
            with get_db_connection() as session:
                exists = session.exec(select(Article).where(Article.url == url)).first()
            
            if exists:
                skipped_existing += 1
                continue
            
            # Salvar apenas metadados (sem chamar API)
            from database import add_article
            
            article_id = add_article(
                url=url,
                title=title,
                published_date=published_date,
                feed_source=feed_source,
                raw_content=None,
                feed_profile=feed_profile,
                url_encoding=url_encoding,
                image_url=None,
                initial_filter_score=None,
                rss_description=description
            )
            
            if article_id:
                new_articles_count += 1
                logger.info(f"  Salvo: {title[:60]}...")
    
    logger.info(f"--- Metadados coletados: {new_articles_count} novos, {skipped_existing} já existiam [{feed_profile}] ---")
    return new_articles_count


def batch_filter(feed_profile: str = None):
    """
    Fase 2 do pipeline batch: filtra artigos pendentes via Batch API.
    
    Busca artigos com initial_filter_score=NULL, envia para avaliação em batch,
    e atualiza os scores no banco.
    """
    import importlib
    import re
    from database import get_articles_pending_filter, update_article_filter_score
    
    logger.info(f"--- [BATCH] Iniciando filtro batch [{feed_profile or 'TODOS'}] ---")
    
    # 1. Buscar artigos pendentes
    pendentes = get_articles_pending_filter(feed_profile)
    
    if not pendentes:
        logger.info("Nenhum artigo pendente de filtro")
        return {"total": 0, "aprovados": 0, "rejeitados": 0, "erros": 0}
    
    logger.info(f"Encontrados {len(pendentes)} artigos pendentes")
    

    # 2. Agrupar por feed_profile para carregar prompts específicos
    artigos_por_feed = {}
    for art in pendentes:
        fp = art['feed_profile']
        if fp not in artigos_por_feed:
            artigos_por_feed[fp] = []
        artigos_por_feed[fp].append(art)
    

    # 3. Montar requests com prompt específico de cada feed
    requests_list = []
    
    for fp, artigos in artigos_por_feed.items():
        # Carregar config do feed
        try:
            feed_config = importlib.import_module(f"feeds.{fp}")
        except ImportError:
            logger.warning(f"Config não encontrada para feed '{fp}', usando default")
            feed_config = None
        
        # Pegar prompt e modelo
        prompt_template = getattr(
            feed_config, 
            'PROMPT_INITIAL_FILTER',
            """Avalie rapidamente se este artigo parece relevante.

            Título: {title}
            Descrição: {description}

            Score de 1 a 5:
            1 = Irrelevante
            2 = Provavelmente irrelevante  
            3 = Pode ser relevante
            4 = Provavelmente relevante
            5 = Claramente relevante

            Responda APENAS com o número (1-5)."""
        )
        
        filter_model = getattr(feed_config, 'FILTER_MODEL', None) or config.FILTER_MODEL
        
        # Montar request para cada artigo
        for art in artigos:
            prompt = prompt_template.format(
                feed_profile=fp,
                title=art['title'] or "Sem título",
                description=art['rss_description'] or "Sem descrição"
            )
            
            requests_list.append({
                "custom_id": f"{fp}-{art['id']}",
                "model": filter_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10
            })
    
    logger.info(f"Montados {len(requests_list)} requests para batch")
    

    # 4. Executar batch
    resultados = executar_batch(requests_list, description="filter")
    
    if resultados is None:
        logger.error("Falha ao executar batch de filtro")
        return {"total": len(pendentes), "aprovados": 0, "rejeitados": 0, "erros": len(pendentes)}
    

    # 5. Processar resultados e atualizar banco
    stats = {"total": len(pendentes), "aprovados": 0, "rejeitados": 0, "erros": 0}
    
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
        
        # Parsear score da resposta
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
    
    
    # Contar erros (artigos sem resposta)
    respondidos = len(resultados)
    stats["erros"] = len(pendentes) - respondidos
    
    logger.info(f"--- Filtro batch concluído: {stats} ---")
    return stats


def fetch_approved_content(feed_profile: str = None):
    """
    Fase 3 do pipeline batch: busca conteúdo dos artigos aprovados no filtro.
    
    Para artigos com initial_filter_score >= 3 e raw_content=NULL:
    - Tenta buscar via Marreta
    - Valida conteúdo (tamanho, paywall, truncamento)
    - Se falhar validação → marca score=1 (rejeitado)
    - Se passar → salva raw_content, image_url
    """
    from database import (
        get_approved_articles_without_content,
        update_article_content,
        update_article_filter_score
    )
    from utils import fetch_article_content_and_og_image
    import time
    
    logger.info(f"--- [BATCH] Buscando conteúdo [{feed_profile or 'TODOS'}] ---")
    
    # 1. Buscar artigos aprovados sem conteúdo
    artigos = get_approved_articles_without_content(feed_profile)
    
    if not artigos:
        logger.info("Nenhum artigo aprovado pendente de conteúdo")
        return {"total": 0, "sucesso": 0, "falha_fetch": 0, "falha_validacao": 0}
    
    logger.info(f"Encontrados {len(artigos)} artigos para buscar conteúdo")
    
    stats = {"total": len(artigos), "sucesso": 0, "falha_fetch": 0, "falha_validacao": 0}
    
    MIN_CONTENT_LENGTH = 500
    PAYWALL_INDICATORS = [
        'subscribe to continue reading',
        'this content is for subscribers',
        'sign up to read more',
        'become a member to',
        'subscribe for full access',
        'continue reading for',
    ]
    
    for art in artigos:
        article_id = art['id']
        url = art['url']
        url_encoding = art['url_encoding']
        title = art['title'] or "Sem título"
        
        logger.info(f"  Buscando: {title[:60]}...")
        
        # 2. Tentar buscar conteúdo
        try:
            fetch_result, marreta = fetch_article_content_and_og_image(url, url_encoding)
            raw_content = fetch_result['content']
            og_image = fetch_result['og_image']
        except Exception as e:
            logger.warning(f"    Erro ao buscar {url}: {e}")
            stats["falha_fetch"] += 1
            continue
        
        # 3. Validar conteúdo
        
        # 3a. Conteúdo vazio ou muito curto
        if not raw_content or len(raw_content) < MIN_CONTENT_LENGTH:
            logger.warning(f"    Conteúdo muito curto ({len(raw_content) if raw_content else 0} chars)")
            update_article_filter_score(article_id, 1)  # Marca como rejeitado
            stats["falha_validacao"] += 1
            continue
        
        # 3b. Detecção de paywall
        content_lower = raw_content[-200:].lower()
        paywall_detected = False
        for indicator in PAYWALL_INDICATORS:
            if indicator in content_lower:
                logger.warning(f"    Paywall detectado: '{indicator}'")
                paywall_detected = True
                break
        
        if paywall_detected:
            update_article_filter_score(article_id, 1)
            stats["falha_validacao"] += 1
            continue
        
        # 3c. Conteúdo truncado
        content_tail = raw_content[-50:].strip()
        last_char = content_tail[-1] if content_tail else ''
        
        if last_char.isalnum() and len(raw_content) < 2000:
            last_words = content_tail.split()[-3:]
            if len(last_words) > 0 and len(last_words[-1]) < 3:
                logger.warning(f"    Conteúdo aparenta estar truncado")
                update_article_filter_score(article_id, 1)
                stats["falha_validacao"] += 1
                continue
        
        # 4. Buscar imagem do RSS se não tiver og:image
        # (simplificado - usa só og:image por enquanto)
        final_image_url = og_image
        
        # 5. Salvar conteúdo
        update_article_content(article_id, raw_content, final_image_url, marreta)
        logger.info(f"    ✓ Conteúdo salvo ({len(raw_content)} chars)")
        stats["sucesso"] += 1
        
        # Rate limiting - ser educado com os servidores
        time.sleep(0.5)
    
    logger.info(f"--- Busca de conteúdo concluída: {stats} ---")
    return stats


def batch_summary(feed_profile: str = None):
    """
    Fase 4a do pipeline batch: sumariza artigos via Batch API.
    
    Busca artigos com raw_content mas sem processed_content,
    envia para sumarização em batch, e salva os resumos.
    """
    import importlib
    from database import get_articles_pending_summary, update_article_processing
    
    logger.info(f"--- [BATCH] Iniciando sumarização [{feed_profile or 'TODOS'}] ---")
    
    # 1. Buscar artigos pendentes
    pendentes = get_articles_pending_summary(feed_profile)
    
    if not pendentes:
        logger.info("Nenhum artigo pendente de sumarização")
        return {"total": 0, "sucesso": 0, "erros": 0}
    
    logger.info(f"Encontrados {len(pendentes)} artigos para sumarizar")
    
    # 2. Agrupar por feed_profile
    artigos_por_feed = {}
    for art in pendentes:
        fp = art['feed_profile']
        if fp not in artigos_por_feed:
            artigos_por_feed[fp] = []
        artigos_por_feed[fp].append(art)
    
    # 3. Montar requests com prompt específico de cada feed
    requests_list = []
    
    for fp, artigos in artigos_por_feed.items():
        # Carregar config do feed
        try:
            feed_config = importlib.import_module(f"feeds.{fp}")
        except ImportError:
            feed_config = None
        
        # Pegar prompt e modelo
        prompt_template = getattr(
            feed_config,
            'PROMPT_ARTICLE_SUMMARY',
            config.PROMPT_ARTICLE_SUMMARY
        )
        
        summary_model = getattr(feed_config, 'SUMMARY_MODEL', None) or config.SUMMARY_MODEL
        
        # Montar request para cada artigo
        for art in artigos:
            prompt = prompt_template.format(
                article_content=art['raw_content'][:4000]  # Limitar contexto
            )
            
            requests_list.append({
                "custom_id": f"{fp}-{art['id']}",
                "model": summary_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": 3000
            })
    
    logger.info(f"Montados {len(requests_list)} requests para batch de sumarização")
    
    # 4. Executar batch
    resultados = executar_batch(requests_list, description="summary")
    
    if resultados is None:
        logger.error("Falha ao executar batch de sumarização")
        return {"total": len(pendentes), "sucesso": 0, "erros": len(pendentes)}
    
    # 5. Processar resultados e atualizar banco
    stats = {"total": len(pendentes), "sucesso": 0, "erros": 0}
    
    for custom_id, resumo in resultados.items():
        # Extrair article_id do custom_id
        parts = custom_id.rsplit("-", 1)
        if len(parts) != 2:
            stats["erros"] += 1
            continue
        
        try:
            article_id = int(parts[1])
        except ValueError:
            stats["erros"] += 1
            continue
        
        # Salvar resumo (sem embedding por enquanto)
        update_article_processing(article_id, resumo, embedding=None)
        stats["sucesso"] += 1
    
    # Contar erros (artigos sem resposta)
    stats["erros"] += len(pendentes) - len(resultados)
    
    logger.info(f"--- Sumarização batch concluída: {stats} ---")
    return stats


def batch_embedding(feed_profile: str = None):
    """
    Fase 4b do pipeline batch: gera embeddings via Batch API.
    
    Busca artigos com processed_content mas sem embedding,
    envia para embedding em batch, e salva os vetores.
    """
    from database import get_articles_pending_embedding, update_article_embedding
    
    logger.info(f"--- [BATCH] Iniciando embeddings [{feed_profile or 'TODOS'}] ---")
    
    # 1. Buscar artigos pendentes
    pendentes = get_articles_pending_embedding(feed_profile)
    
    if not pendentes:
        logger.info("Nenhum artigo pendente de embedding")
        return {"total": 0, "sucesso": 0, "erros": 0}
    
    logger.info(f"Encontrados {len(pendentes)} artigos para embedding")
    
    # 2. Montar requests (mesmo modelo para todos)
    requests_list = []
    
    for art in pendentes:
        requests_list.append({
            "custom_id": f"{art['feed_profile']}-{art['id']}",
            "body": {
                "model": config.EMBEDDING_MODEL,
                "input": art['processed_content']
            }
        })
    
    logger.info(f"Montados {len(requests_list)} requests para batch de embedding")
    
    # 3. Executar batch (endpoint diferente!)
    resultados = executar_batch(
        requests_list, 
        description="embedding",
        endpoint="/v1/embeddings",
        is_embedding=True
    )
    
    if resultados is None:
        logger.error("Falha ao executar batch de embedding")
        return {"total": len(pendentes), "sucesso": 0, "erros": len(pendentes)}
    
    # 4. Processar resultados e atualizar banco
    stats = {"total": len(pendentes), "sucesso": 0, "erros": 0}
    
    for custom_id, embedding in resultados.items():
        # Extrair article_id do custom_id
        parts = custom_id.rsplit("-", 1)
        if len(parts) != 2:
            stats["erros"] += 1
            continue
        
        try:
            article_id = int(parts[1])
        except ValueError:
            stats["erros"] += 1
            continue
        
        # Salvar embedding
        update_article_embedding(article_id, embedding)
        stats["sucesso"] += 1
    
    # Contar erros (artigos sem resposta)
    stats["erros"] += len(pendentes) - len(resultados)
    
    logger.info(f"--- Embedding batch concluído: {stats} ---")
    return stats


def batch_rating(feed_profile: str = None):
    """
    Fase 5 do pipeline batch: avalia impacto dos artigos via Batch API.
    
    Busca artigos com embedding mas sem impact_score,
    envia para avaliação em batch, e salva os scores.
    """
    import importlib
    import re
    from database import get_articles_pending_rating, update_article_rating
    
    logger.info(f"--- [BATCH] Iniciando rating [{feed_profile or 'TODOS'}] ---")
    
    # 1. Buscar artigos pendentes
    pendentes = get_articles_pending_rating(feed_profile)
    
    if not pendentes:
        logger.info("Nenhum artigo pendente de rating")
        return {"total": 0, "sucesso": 0, "erros": 0}
    
    logger.info(f"Encontrados {len(pendentes)} artigos para avaliar")
    
    # 2. Agrupar por feed_profile
    artigos_por_feed = {}
    for art in pendentes:
        fp = art['feed_profile']
        if fp not in artigos_por_feed:
            artigos_por_feed[fp] = []
        artigos_por_feed[fp].append(art)
    
    # 3. Montar requests com prompt específico de cada feed
    requests_list = []
    
    for fp, artigos in artigos_por_feed.items():
        # Carregar config do feed
        try:
            feed_config = importlib.import_module(f"feeds.{fp}")
        except ImportError:
            feed_config = None
        
        # Pegar prompt e modelo
        prompt_template = getattr(
            feed_config,
            'PROMPT_IMPACT_RATING',
            config.PROMPT_IMPACT_RATING
        )
        
        rating_model = getattr(feed_config, 'RATING_MODEL', None) or config.RATING_MODEL
        
        # Montar request para cada artigo
        for art in artigos:
            prompt = prompt_template.format(
                summary=art['processed_content']
            )
            
            requests_list.append({
                "custom_id": f"{fp}-{art['id']}",
                "model": rating_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": 1000
            })
    
    logger.info(f"Montados {len(requests_list)} requests para batch de rating")
    
    # 4. Executar batch
    resultados = executar_batch(requests_list, description="rating")
    
    if resultados is None:
        logger.error("Falha ao executar batch de rating")
        return {"total": len(pendentes), "sucesso": 0, "erros": len(pendentes)}
    
    # 5. Processar resultados e atualizar banco
    stats = {"total": len(pendentes), "sucesso": 0, "erros": 0}
    
    for custom_id, resposta in resultados.items():
        # Extrair article_id do custom_id
        parts = custom_id.rsplit("-", 1)
        if len(parts) != 2:
            stats["erros"] += 1
            continue
        
        try:
            article_id = int(parts[1])
        except ValueError:
            stats["erros"] += 1
            continue
        
        # Parsear score (1-10)
        match = re.search(r'\b([1-9]|10)\b', resposta.strip())
        if match:
            score = int(match.group(1))
            update_article_rating(article_id, score)
            stats["sucesso"] += 1
        else:
            logger.warning(f"Score inválido para {custom_id}: '{resposta}'")
            stats["erros"] += 1
    
    # Contar erros (artigos sem resposta)
    stats["erros"] += len(pendentes) - len(resultados)
    
    logger.info(f"--- Rating batch concluído: {stats} ---")
    return stats



def executar_pipeline_batch():
    """
    Executa o pipeline completo de preparação de artigos via Batch API.
    Processa TODOS os feeds ativos de uma vez.
    
    Fases:
    1. Coleta metadados do RSS (loop por cada feed)
    2. Filtra artigos via batch (todos juntos)
    3. Busca conteúdo dos aprovados (todos juntos)
    4a. Sumariza via batch (todos juntos, prompts específicos por feed)
    4b. Gera embeddings via batch (todos juntos)
    5. Avalia impacto via batch (todos juntos, prompts específicos por feed)
    
    Após isso, os artigos estão prontos para gerar briefing.
    """
    import importlib
    
    logger.info(f"{'='*60}")
    logger.info(f"PIPELINE BATCH - TODOS OS FEEDS")
    logger.info(f"{'='*60}")
    
    # Fase 1: Coletar metadados de cada feed
    logger.info(f"\n>>> FASE 1: Coleta de metadados RSS <<<")
    
    feeds_ativos = get_active_feeds()
    logger.info(f"Feeds ativos encontrados: {feeds_ativos}")
    
    total_novos = 0
    novos_por_feed = {}
    
    for feed_name in feeds_ativos:
        try:
            feed_config = importlib.import_module(f"feeds.{feed_name}")
            rss_feeds = getattr(feed_config, 'RSS_FEEDS', [])
            
            if not rss_feeds:
                logger.warning(f"  {feed_name}: Nenhum RSS_FEEDS definido")
                continue
            
            novos = scrape_metadata_only(feed_name, rss_feeds, feed_config)
            novos_por_feed[feed_name] = novos
            total_novos += novos
            
        except ImportError as e:
            logger.error(f"  {feed_name}: Erro ao carregar config - {e}")
    
    logger.info(f"Fase 1 concluída: {total_novos} novos artigos")
    logger.info(f"  Por feed: {novos_por_feed}")
    
    # Fase 2: Filtrar via batch (todos os feeds juntos)
    logger.info(f"\n>>> FASE 2: Filtro batch <<<")
    stats_filter = batch_filter(feed_profile=None)
    logger.info(f"Fase 2 concluída: {stats_filter}")
    
    # Fase 3: Buscar conteúdo (todos os feeds juntos)
    logger.info(f"\n>>> FASE 3: Busca de conteúdo <<<")
    stats_content = fetch_approved_content(feed_profile=None)
    logger.info(f"Fase 3 concluída: {stats_content}")
    
    # Fase 4a: Sumarizar via batch (todos os feeds juntos)
    logger.info(f"\n>>> FASE 4a: Sumarização batch <<<")
    stats_summary = batch_summary(feed_profile=None)
    logger.info(f"Fase 4a concluída: {stats_summary}")
    
    # Fase 4b: Embeddings via batch (todos os feeds juntos)
    logger.info(f"\n>>> FASE 4b: Embeddings batch <<<")
    stats_embedding = batch_embedding(feed_profile=None)
    logger.info(f"Fase 4b concluída: {stats_embedding}")
    
    # Fase 5: Rating via batch (todos os feeds juntos)
    logger.info(f"\n>>> FASE 5: Rating batch <<<")
    stats_rating = batch_rating(feed_profile=None)
    logger.info(f"Fase 5 concluída: {stats_rating}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"PIPELINE BATCH CONCLUÍDO")
    logger.info(f"{'='*60}")
    
    return {
        "feeds_processados": feeds_ativos,
        "novos_artigos": total_novos,
        "novos_por_feed": novos_por_feed,
        "filter": stats_filter,
        "content": stats_content,
        "summary": stats_summary,
        "embedding": stats_embedding,
        "rating": stats_rating
    }