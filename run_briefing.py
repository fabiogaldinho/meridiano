# simple-meridian/run_briefing.py

import os
import importlib
import feedparser
from datetime import datetime, timedelta
import json
import time
import re
import numpy as np
from sklearn.cluster import KMeans
from dotenv import load_dotenv
import anthropic
import openai
import argparse

from utils import fetch_article_content_and_og_image

try:
    import config_base as config # Load base config first
except ImportError:
    print("ERROR: config_base.py not found. Please ensure it exists.")
    exit(1)

import database
from models import Article
from db import get_db_connection
from sqlmodel import select, func

# --- Setup ---
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = anthropic.Anthropic(api_key=API_KEY)
embedding_client = openai.Client(api_key=OPENAI_API_KEY)
openai_chat_client = openai.Client(api_key=OPENAI_API_KEY)


def send_telegram_notification(chat_id, message, parse_mode='HTML'):
    """
    Envia notificação push via Telegram bot.
    
    Args:
        message: O texto da mensagem a ser enviada
        parse_mode: Formato do texto - 'HTML' ou 'Markdown'
    
    A função falha silenciosamente se as credenciais não estiverem configuradas
    ou se houver erro ao enviar, para não quebrar o pipeline principal.
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token or not chat_id:
        return
    
    try:
        import requests
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"Telegram notification sent successfully")
        else:
            print(f"Warning: Telegram notification failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Warning: Failed to send Telegram notification: {e}")


def get_deepseek_embedding(text, model=config.EMBEDDING_MODEL):
    """Gets embeddings."""
    print(f"INFO: Attempting to get embedding for text snippet: '{text[:50]}...'")

    try:
         response = embedding_client.embeddings.create(
             model=model, # Use the actual model name from Deepseek docs
             input=[text] # API likely expects a list of strings
         )
         # Access the embedding vector based on the actual API response structure
         if response.data and len(response.data) > 0:
              embedding = response.data[0].embedding
              # Validate embedding is not empty and has valid structure
              if embedding and len(embedding) > 0:
                  return embedding
              else:
                  print(f"Warning: Empty or invalid embedding returned for text.")
                  return None
         else:
              print(f"Warning: No embedding data in API response.")
              return None
    except Exception as e:
         print(f"Error calling Embedding API: {e}")
         return None
    

def call_llm(prompt, model, system_prompt=None, max_tokens=2048, temperature=0.7):
    """Calls the Claude API for chat completion."""

    max_retries = 3
    base_wait_time = 2

    fallback_model = None
    if model == "gpt-5-nano":
        fallback_model = "gpt-5-mini"
        print(f"  Fallback model configured: {fallback_model}")
    
    result = _attempt_llm_call(prompt, model, system_prompt, max_tokens, temperature, max_retries, base_wait_time)

    if result is None and fallback_model:
        print(f"  ⚠ All attempts with {model} failed. Trying fallback model {fallback_model}...")
        
        fallback_retries = 2
        result = _attempt_llm_call(prompt, fallback_model, system_prompt, max_tokens, 
                                   temperature, fallback_retries, base_wait_time)
        
        if result is not None:
            print(f"  ✓ Fallback successful with {fallback_model}")
        else:
            print(f"  ✗ Fallback also failed with {fallback_model}")
    

    return result


def _attempt_llm_call(prompt, model, system_prompt, max_tokens, temperature, max_retries, base_wait_time):
    """
    Tenta fazer uma chamada LLM com retries.
    Esta é uma função auxiliar usada por call_llm.
    
    Retorna:
        str: O conteúdo da resposta se bem-sucedido, None se falhou
    """
    
    for attempt in range(max_retries):
        if attempt > 0:
            wait_time = base_wait_time * (2 ** (attempt - 1))  # Backoff exponencial
            print(f"  Retry attempt {attempt + 1}/{max_retries} after {wait_time}s wait...")
            time.sleep(wait_time)

        if model.startswith("gpt"):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = openai_chat_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens
                )

                content = response.choices[0].message.content
                result = content.strip() if content else None

                if result:
                    if attempt > 0:
                        print(f"  ✓ Retry successful on attempt {attempt + 1}")
                    return result

                if attempt == max_retries - 1:
                    print(f"  Empty response on attempt {attempt + 1}/{max_retries} with {model}")
                else:
                    print(f"  Empty response on attempt {attempt + 1}, will retry...")

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"  Error on attempt {attempt + 1}/{max_retries} with {model}: {e}")
                else:
                    print(f"  Error on attempt {attempt + 1}: {e}, will retry...")
                time.sleep(1)
            

        elif model.startswith("claude"):
            try:
                if system_prompt:
                    response = client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                else:
                    response = client.messages.create(
                        model=model,
                        max_tokens=2048,
                        temperature=0.7,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                return response.content[0].text.strip()                                         # type: ignore
            
            except Exception as e:
                print(f"Error calling Claude API: {e}")
                time.sleep(1)
                return None
        
        else:
            print(f"Unknown model type: {model}")
            return None
    
    return None


def evaluate_rss_snippet_relevance(title, description, feed_profile, effective_config):
    """
    Evaluates if an RSS entry is worth fetching and processing based on title and snippet.
    Uses a cheap model to make a quick relevance judgment.
    
    Args:
        title: Article title from RSS
        description: Article description/snippet from RSS
        feed_profile: Which feed profile this is for
        effective_config: Config object with prompts and model settings
        
    Returns:
        int: Score from 1-5, or None if evaluation failed
    """
    
    filter_model = getattr(effective_config, 'FILTER_MODEL', config.FILTER_MODEL)
    
    filter_prompt_template = getattr(
        effective_config, 
        'PROMPT_INITIAL_FILTER',
        """Avalie rapidamente se este artigo parece relevante para o tema '{feed_profile}'.

            Título: {title}
            Descrição: {description}

            Baseado APENAS nestas informações, dê um score de 1 a 5:

            1 = Completamente irrelevante, descarte
            2 = Provavelmente irrelevante, mas não tenho certeza
            3 = Pode ser relevante, vale investigar
            4 = Provavelmente relevante
            5 = Claramente relevante e importante

            Seja CONSERVADOR - na dúvida, dê score menor. É melhor descartar um artigo duvidoso que processar muito lixo.

            Responda APENAS com o número (1-5)."""
    )
    
    prompt = filter_prompt_template.format(
        feed_profile=feed_profile,
        title=title or "Sem título",
        description=description or "Sem descrição"
    )
    
    try:
        response = call_llm(
            prompt,
            model=filter_model,
            max_tokens=10
        )
        
        if not response:
            print(f"  Warning: No response from filter model")
            return None
        
        import re
        match = re.search(r'\b([1-5])\b', response.strip())
        if match:
            score = int(match.group(1))
            print(f"  Initial filter score: {score}/5 - {title[:60]}...")
            return score
        else:
            print(f"  Warning: Could not parse filter score from '{response}'")
            return None
            
    except Exception as e:
        print(f"  Error in initial filter evaluation: {e}")
        return None



# --- Core Functions ---

def scrape_articles(feed_profile, rss_feeds, effective_config): # Added params
    """Scrapes articles for a specific feed profile."""
    print(f"\n--- Starting Article Scraping [{feed_profile}] ---")


    with get_db_connection() as session:
        existing_count = session.exec(
            select(func.count(Article.id)).where(Article.feed_profile == feed_profile)
        ).one()
    
    is_cold_start = (existing_count == 0)
    
    if is_cold_start:
        max_age_days = getattr(effective_config, 'SCRAPING_MAX_AGE_DAYS_INITIAL', 7)
        print(f"Cold start detected for '{feed_profile}' - accepting articles up to {max_age_days} days old")
    else:
        max_age_days = getattr(effective_config, 'SCRAPING_MAX_AGE_DAYS_NORMAL', 3)
        print(f"Normal execution for '{feed_profile}' - accepting articles up to {max_age_days} days old")
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)


    new_articles_count = 0
    if not rss_feeds:
        print(f"Warning: No RSS_FEEDS defined for profile '{feed_profile}'. Skipping scrape.")
        return

    for feed_url in rss_feeds:
        print(f"Fetching feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        if feed.bozo: print(f"Warning: Potential issue parsing feed {feed_url}: {feed.bozo_exception}")

        for entry in feed.entries:
            replaces = [
                ("/", "%2F"),
                (":", "%3A"),
                (" ", "%20"),
                ("?", "%3F"),
                ("&", "%26"),
                ("=", "%3D"),
                ("#", "%23")
            ]

            url = entry.get('link')
            url_encoding = url

            for old, new in replaces:
                url_encoding = url_encoding.replace(old, new)                                       # type: ignore
            
            url_encoding = "https://marreta.galdinho.news/p/" + url_encoding                        # type: ignore


            title = entry.get('title', 'No Title')
            description = entry.get('description', '') or entry.get('summary', '')
            published_parsed = entry.get('published_parsed')
            published_date = datetime(*published_parsed[:6]) if published_parsed else datetime.now()                    # type: ignore
            feed_source = feed.feed.get('title', feed_url)                                                              # type: ignore

            if not url: continue

            if published_date < cutoff_date:
                print(f"  Skipping old article from {published_date.strftime('%Y-%m-%d')}: {title[:60]}...")            # type: ignore
                continue

            # --- Check if article exists ---
            with get_db_connection() as session:
                exists = session.exec(select(Article).where(Article.url == url)).first()
            if exists: continue
            # --- End Check ---


            # FILTRO INICIAL - Avaliar se vale a pena processar este artigo
            print(f"Evaluating: {title[:70]}...")

            min_filter_score = getattr(effective_config, 'MIN_INITIAL_FILTER_SCORE', 3)

            filter_score = evaluate_rss_snippet_relevance(
                title, 
                description, 
                feed_profile,
                effective_config
            )

            if filter_score is None:
                filter_score = 3
                print(f"  Filter evaluation failed, assuming score 3")

            if filter_score < min_filter_score:
                print(f"  FILTERED OUT (score {filter_score} < {min_filter_score})")

                database.add_article(
                    url=url,
                    title=title,
                    published_date=published_date,
                    feed_source=feed_source,
                    raw_content=None,
                    feed_profile=feed_profile,
                    url_encoding=url_encoding,
                    image_url=None,
                    initial_filter_score=filter_score
                )

                continue

            print(f"  PASSED filter (score {filter_score} >= {min_filter_score})")


            print(f"Processing new entry: {title} ({url})")

            # --- 1. Try getting image from RSS feed ---
            rss_image_url = None
            # Check enclosures
            if 'enclosures' in entry:
                for enc in entry.enclosures:
                    if enc.get('type', '').startswith('image/'):
                        rss_image_url = enc.get('href')
                        break # Take the first image enclosure
            # Check media_content if no enclosure image found
            if not rss_image_url and 'media_content' in entry:
                 for media in entry.media_content:
                     if media.get('medium') == 'image' and media.get('url'):
                          rss_image_url = media.get('url')
                          break # Take the first media image
                     elif media.get('type', '').startswith('image/') and media.get('url'):
                          rss_image_url = media.get('url')
                          break
            # Check simple image tag (less common)
            if not rss_image_url and 'image' in entry and isinstance(entry.image, dict) and entry.image.get('url'):
                rss_image_url = entry.image.get('url')

            if rss_image_url:
                print(f"  Found image in RSS: {rss_image_url[:60]}...")
            # --- End RSS Image Check ---

            # --- 2. Fetch Article Content & OG Image ---
            print(f"  Fetching article content and OG image...")
            fetch_result, marreta = fetch_article_content_and_og_image(url, url_encoding)
            raw_content = fetch_result['content']
            og_image_url = fetch_result['og_image']
            # --- End Fetch ---

            if not raw_content:
                print(f"  Skipping article, failed to extract main content: {title}")
                continue

            MIN_CONTENT_LENGTH = 500
            if len(raw_content) < MIN_CONTENT_LENGTH:
                print(f"  FILTERED: Content too short ({len(raw_content)} chars, minimum {MIN_CONTENT_LENGTH})")
                print(f"  Skipping: {title[:70]}...")
                # Salva no banco com initial_filter_score baixo para não tentar de novo
                database.add_article(
                    url=url,
                    title=title,
                    published_date=published_date,
                    feed_source=feed_source,
                    raw_content=None,
                    feed_profile=feed_profile,
                    url_encoding=url_encoding,
                    image_url=None,
                    initial_filter_score=1,
                    marreta=marreta
                )
                continue


            content_tail = raw_content[-50:].strip()
            last_char = content_tail[-1] if content_tail else ''

            if last_char.isalnum():
                last_words = content_tail.split()[-3:]
                last_fragment = ' '.join(last_words)

                if len(last_words[-1]) < 3 and len(raw_content) < 3000:
                    print(f"  WARNING: Article appears truncated (ends with: '...{content_tail[-30:]}')")
                    print(f"  Content length: {len(raw_content)} chars")
                    print(f"  Skipping: {title[:70]}...")
                    
                    database.add_article(
                        url=url,
                        title=title,
                        published_date=published_date,
                        feed_source=feed_source,
                        raw_content=None,
                        feed_profile=feed_profile,
                        url_encoding=url_encoding,
                        image_url=None,
                        initial_filter_score=1,
                        marreta=marreta
                    )
                    continue

                
                if len(raw_content) < 2000:
                    print(f"  WARNING: Short article ending without punctuation")
                    print(f"  Last fragment: '...{content_tail[-30:]}'")
                    print(f"  Will attempt to process, but may be incomplete")

            
            paywall_indicators = [
                'subscribe to continue reading',
                'this content is for subscribers',
                'sign up to read more',
                'become a member to',
                'subscribe for full access',
                'continue reading for',
            ]

            content_lower = raw_content[-200:].lower()  # Últimos 200 chars em lowercase
            for indicator in paywall_indicators:
                if indicator in content_lower:
                    print(f"  FILTERED: Paywall detected ('{indicator}')")
                    print(f"  Skipping: {title[:70]}...")
                    database.add_article(
                        url=url,
                        title=title,
                        published_date=published_date,
                        feed_source=feed_source,
                        raw_content=None,
                        feed_profile=feed_profile,
                        url_encoding=url_encoding,
                        image_url=None,
                        initial_filter_score=1,
                        marreta=marreta
                    )
                    continue


            # Se chegou aqui, o conteúdo passou em todas as verificações
            print(f"  ✓ Content validation passed ({len(raw_content)} chars)")
                        

            # --- 3. Determine Final Image URL and Save ---
            final_image_url = rss_image_url if rss_image_url else og_image_url
            if final_image_url:
                 print(f"  Using image URL: {final_image_url[:60]}...")
            else:
                 print("  No image found in RSS or OG tags.")

            article_id = database.add_article(
                url, title, published_date, feed_source, raw_content,
                feed_profile,
                url_encoding,
                final_image_url,
                initial_filter_score=filter_score,
                marreta=marreta)
            if article_id: new_articles_count += 1
            time.sleep(0.5) # Be polite

    print(f"--- Scraping Finished [{feed_profile}]. Added {new_articles_count} new articles. ---")


def process_articles(feed_profile, effective_config):
    """Processes unprocessed articles: summarizes and generates embeddings."""
    print("\n--- Starting Article Processing ---")
    summary_model = getattr(effective_config, 'SUMMARY_MODEL', config.SUMMARY_MODEL)
    summary_prompt_template = getattr(effective_config, 'PROMPT_ARTICLE_SUMMARY', config.PROMPT_ARTICLE_SUMMARY)

    unprocessed = database.get_unprocessed_articles(feed_profile, 1000)
    processed_count = 0
    if not unprocessed:
        print("No new articles to process.")
        return

    print(f"Found {len(unprocessed)} articles to process.")
    for article in unprocessed:
        print(f"Processing article ID: {article['id']} - {article['url'][:50]}...")

        # 1. Summarize using Deepseek Chat
        # Format the potentially profile-specific summary prompt
        summary_prompt = summary_prompt_template.format(
            article_content=article['raw_content'][:4000] # Limit context
        )
        summary = call_llm(summary_prompt, model=summary_model)

        if not summary:
            print(f"WARNING: Failed to summarize article {article['id']} after all attempts")

            with database.get_db_connection() as session:
                stmt = select(database.Article).where(database.Article.id == article['id'])
                article_record = session.exec(stmt).first()
                if article_record:
                    article_record.initial_filter_score = 1
                    session.add(article_record)
                    session.commit()
            
            debug_dir = "/app/data/failed_prompts"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_file = f"{debug_dir}/failed_summary_{timestamp}.txt"
            
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(f"Failed Prompt Debug Information\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(f"Model attempted: {summary_model}\n")
                    if summary_model == "gpt-5-nano":
                        f.write(f"Fallback attempted: gpt-5-mini\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Article ID: {article['id']}\n")
                    f.write(f"Article URL: {article['url']}\n")
                    f.write(f"Prompt length: {len(summary_prompt)} characters\n")
                    f.write(f"\n{'='*80}\n")
                    f.write(f"FULL PROMPT:\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(summary_prompt)
                print(f"  Debug prompt saved to: {debug_file}")
            except Exception as e:
                print(f"  Failed to save debug prompt: {e}")

            print(f"Skipping article {article['id']} due to summarization error.")
            continue

        print(f"Article summary is: {summary}")

        # 2. Generate Embedding using Deepseek (or alternative)
        # Use summary for embedding to focus on core topics and save tokens/time
        embedding = get_deepseek_embedding(summary)

        if not embedding:
             print(f"Skipping article {article['id']} due to embedding error.")
             continue # Or store article without embedding if desired

        # 3. Update Database
        database.update_article_processing(article['id'], summary, embedding)
        processed_count += 1
        print(f"Successfully processed article ID: {article['id']}")
        time.sleep(1) # Avoid hitting API rate limits

    print(f"--- Processing Finished. Processed {processed_count} articles. ---")

def rate_articles(feed_profile, effective_config):
    """Rates the impact of processed articles using an LLM."""
    print("\n--- Starting Article Impact Rating ---")
    if not client:
        print("Skipping rating: Deepseek client not initialized.")
        return

    rating_model = getattr(effective_config, 'RATING_MODEL', config.RATING_MODEL)
    rating_prompt_template = getattr(effective_config, 'PROMPT_IMPACT_RATING', config.PROMPT_IMPACT_RATING)

    unrated = database.get_unrated_articles(feed_profile, 1000)
    rated_count = 0
    if not unrated:
        print("No new articles to rate.")
        return

    print(f"Found {len(unrated)} processed articles to rate.")
    for article in unrated:
        print(f"Rating article ID: {article['id']}: {article['title']}...")
        summary = article['processed_content']
        if not summary:
            print(f"  Skipping article {article['id']} - no summary found.")
            continue

        # Format the potentially profile-specific rating prompt
        rating_prompt = rating_prompt_template.format(
            summary=summary
        )
        rating_response = call_llm(rating_prompt, model=rating_model)

        impact_score = None
        if rating_response:
            try:
                # Extract first integer (1-10) from response using regex
                # This handles multi-line responses and text around the number
                match = re.search(r'\b([1-9]|10)\b', rating_response.strip())
                if match:
                    score = int(match.group(1))
                    if 1 <= score <= 10:
                        impact_score = score
                        print(f"  Article ID {article['id']} rated as: {impact_score}")
                    else:
                        print(f"  Warning: Rating response '{rating_response}' for article {article['id']} is out of range (1-10).")
                else:
                    print(f"  Warning: Could not find valid rating (1-10) in response '{rating_response}' for article {article['id']}.")
            except (ValueError, AttributeError) as e:
                print(f"  Warning: Could not parse integer rating from response '{rating_response}' for article {article['id']}: {e}")
        else:
            print(f"  Warning: No rating response received for article {article['id']}.")

        # Update database even if rating failed (impact_score will be None, prevents re-attempting failed ones immediately)
        # Or only update if impact_score is not None:
        if impact_score is not None:
             database.update_article_rating(article['id'], impact_score)
             rated_count += 1
        # else: # Decide if you want to mark failed attempts differently
             # database.update_article_rating(article['id'], -1) # Example: Mark as failed with -1? Or leave NULL? Leaving NULL for now.

        time.sleep(1) # API rate limiting

    print(f"--- Rating Finished. Rated {rated_count} articles. ---")

def append_article_references(brief_markdown, articles, feed_profile):
    """
    Appends a "References" section to the briefing with links to source articles.
    
    Args:
        brief_markdown (str): The generated briefing text
        articles (list): List of article dictionaries used in the briefing
        feed_profile (str): The feed profile name
    
    Returns:
        str: The briefing with references section appended
    """
    references_section = "\n\n---\n\n## Artigos de Referência\n\n"
    references_section += f"Este briefing foi gerado a partir de {len(articles)} artigos:\n\n"
    
    sorted_articles = sorted(
        articles,
        key=lambda x: (
            x.get('impact_score') is not None,
            x.get('impact_score') or 0
        ),
        reverse=True
    )
    
    # Adicionar cada artigo como item da lista
    for i, article in enumerate(sorted_articles, 1):
        title = article.get('title', 'Sem título')
        url = article.get('url', '#')
        source = article.get('feed_source', 'Fonte desconhecida')
        impact = article.get('impact_score')
        published = article.get('published_date')
        url_encoding = article.get('url_encoding', '#')
        marreta = article.get('marreta')
        
        date_str = ""
        if published:
            if isinstance(published, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d/%m/%Y')
                except:
                    date_str = published
            else:
                date_str = published.strftime('%d/%m/%Y')
        
        if (marreta):
            ref_line = f'{i}. <strong><a href="{url_encoding}" target="_blank" rel="noopener noreferrer">{title}</a></strong>'
        else:
            ref_line = f'{i}. <strong><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></strong>'
        
        metadata_parts = []
        if source:
            metadata_parts.append(source)
        if date_str:
            metadata_parts.append(date_str)
        if impact is not None:
            metadata_parts.append(f"Impacto: {impact}/10")
        
        if metadata_parts:
            ref_line += f" - *{' | '.join(metadata_parts)}*"
        
        references_section += ref_line + "\n"
    
    return brief_markdown + references_section




def generate_brief(feed_profile, effective_config): # Added feed_profile param
    """Generates the briefing for a specific feed profile."""
    print(f"\n--- Starting Brief Generation [{feed_profile}] ---")
    # Get articles *for this specific profile*
    min_impact_score = getattr(effective_config, 'MIN_IMPACT_SCORE_FOR_BRIEFING', 5)

    # Get articles que ainda não foram analisados
    articles = database.get_articles_for_briefing(
        feed_profile,
        min_impact_score
    )

    if not articles:
        print(f"No new articles available for briefing [{feed_profile}].")
        print("Skipping brief generation - all recent articles already used.")
        return
    
    min_articles = getattr(effective_config, 'MIN_ARTICLES_FOR_BRIEFING', config.MIN_ARTICLES_FOR_BRIEFING)

    if len(articles) < min_articles:
        print(f"Not enough NEW articles ({len(articles)}) for profile '{feed_profile}'.")
        print(f"Minimum required: {min_articles}.")
        print("Skipping brief generation.")
        return

    print(f"Generating brief from {len(articles)} NEW articles.")

    # Prepare data for clustering
    article_ids = [a['id'] for a in articles]
    summaries = [a['processed_content'] for a in articles]
    embeddings = [json.loads(a['embedding']) for a in articles if a['embedding']] # Load JSON string

    if len(embeddings) != len(articles):
        print("Warning: Some articles selected for briefing are missing embeddings. Proceeding with available ones.")
        # Filter articles, summaries, ids to match embeddings
        valid_indices = [i for i, a in enumerate(articles) if a['embedding']]
        articles = [articles[i] for i in valid_indices]
        article_ids = [article_ids[i] for i in valid_indices]
        summaries = [summaries[i] for i in valid_indices]
        # embeddings are already filtered

    if len(embeddings) < min_articles:
         print(f"Not enough articles ({len(embeddings)}) with embeddings to cluster. Min required: {min_articles}.")
         return

    embedding_matrix = np.array(embeddings)

    # Clustering (using KMeans as an example)
    n_clusters = min(config.N_CLUSTERS, len(embedding_matrix) // 2) # Ensure clusters < samples/2
    if n_clusters < 2 : # Need at least 2 clusters for KMeans typically
        print("Not enough articles to form meaningful clusters. Skipping clustering.")
        # Alternative: Treat all articles as one cluster or generate simple list summary
        # For now, we'll just exit brief generation
        return

    print(f"Clustering {len(embedding_matrix)} articles into {n_clusters} clusters...")
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) # n_init='auto' in newer sklearn
        kmeans.fit(embedding_matrix)
        labels = kmeans.labels_
    except Exception as e:
        print(f"Error during clustering: {e}")
        return

    # Analyze each cluster
    cluster_analyses = []
    print("Analyzing clusters...")

   # *** Get the cluster analysis prompt template from effective_config ***
    cluster_analysis_prompt_template = getattr(
        effective_config,
        'PROMPT_CLUSTER_ANALYSIS',      # Look for this constant
        config.PROMPT_CLUSTER_ANALYSIS # Fallback to default if not found
    )
    print(f"DEBUG: Using Cluster Analysis Prompt Template:\n'''{cluster_analysis_prompt_template[:100]}...'''") # Debug

    cluster_model = getattr(effective_config, 'CLUSTER_MODEL', config.CLUSTER_MODEL)

    for i in range(n_clusters): # Use the actual n_clusters determined
        cluster_indices = np.where(labels == i)[0]
        if len(cluster_indices) == 0: continue # Skip empty clusters

        cluster_summaries = [summaries[idx] for idx in cluster_indices]
        print(f"  Analyzing Cluster {i} ({len(cluster_summaries)} articles)")

        MAX_SUMMARIES_PER_CLUSTER = 10 # Consider making this configurable too?
        cluster_summaries_text = "\n\n".join([f"- {s}" for s in cluster_summaries[:MAX_SUMMARIES_PER_CLUSTER]])

        # *** Format the chosen prompt template ***
        analysis_prompt = cluster_analysis_prompt_template.format(
            cluster_summaries_text=cluster_summaries_text,
            feed_profile=feed_profile
        )

        # *** Call LLM with the formatted prompt ***
        #cluster_analysis = call_deepseek_chat(analysis_prompt) # System prompt could also be configurable
        #cluster_analysis = call_claude_chat(analysis_prompt)
        cluster_analysis = call_llm(analysis_prompt, model=cluster_model)

        if cluster_analysis:
            # (Consider adding more robust filtering of non-analysis responses)
            if "unrelated" not in cluster_analysis.lower() or len(cluster_summaries) > 2:
                 cluster_analyses.append({"topic": f"Cluster {i+1}", "analysis": cluster_analysis, "size": len(cluster_summaries)})
        time.sleep(1) # Rate limiting
    # --- End Analyze each cluster ---

    if not cluster_analyses:
        print("No meaningful clusters found or analyzed.")
        return

    # Sort clusters by size (number of articles) to prioritize major themes
    cluster_analyses.sort(key=lambda x: x['size'], reverse=True)

    # Synthesize Final Brief using profile-specific or default prompt
    brief_synthesis_prompt_template = getattr(effective_config, 'PROMPT_BRIEF_SYNTHESIS', config.PROMPT_BRIEF_SYNTHESIS) # Fallback
    print(f"DEBUG: Using Brief Synthesis Prompt Template:\n'''{brief_synthesis_prompt_template[:100]}...'''") # Debug print

    cluster_analyses_text = ""
    for i, cluster in enumerate(cluster_analyses[:5]):
        cluster_analyses_text += f"--- Cluster {i+1} ({cluster['size']} articles) ---\nAnalysis: {cluster['analysis']}\n\n"
    
    brief_model = getattr(effective_config, 'BRIEF_MODEL', config.BRIEF_MODEL)

    synthesis_prompt = brief_synthesis_prompt_template.format(
        cluster_analyses_text=cluster_analyses_text,
        feed_profile=feed_profile
    )
    final_brief_md = call_llm(synthesis_prompt, model=brief_model)

    if final_brief_md:

        final_brief_md = append_article_references(
            final_brief_md, 
            articles,
            feed_profile
        )

        brief_id = database.save_brief(final_brief_md, article_ids, feed_profile)

        print(f"\nMarking all {len(articles)} considered articles as analyzed...")
        with get_db_connection() as session:
            for article_dict in articles:
                article = session.exec(
                    select(Article).where(Article.id == article_dict['id'])
                ).first()
                
                if article:
                    article.briefing_analyzed = True
                    session.add(article)
            
            session.commit()
        print(f"All {len(articles)} articles marked as analyzed")


        print(f"Adding brief_id to {len(article_ids)} articles included in briefing...")
        with get_db_connection() as session:
            for art_id in article_ids:
                article = session.exec(
                    select(Article).where(Article.id == art_id)
                ).first()
                
                if article:
                    existing_ids = json.loads(article.brief_ids) if article.brief_ids else []
                    if brief_id not in existing_ids:
                        existing_ids.append(brief_id)
                        article.brief_ids = json.dumps(existing_ids)
                        session.add(article)
            
            session.commit()

        print(f"Brief ID {brief_id} added to included articles")

        chat_ids = getattr(effective_config, 'TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
        for chatid, chaturl in chat_ids.items():
            notification_message = f"""
            <b>📰 Novo Briefing Disponível</b>

            <b>Feed:</b> {feed_profile}
            <b>Artigos:</b> {len(articles)}
            <b>ID:</b> {brief_id}

            Acesse em: {chaturl}
            """


            send_telegram_notification(chatid, notification_message)

        print(f"--- Brief Generation Finished Successfully [{feed_profile}] ---")
    else:
        print(f"--- Brief Generation Failed [{feed_profile}]: Could not synthesize final brief. ---")

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Meridian Briefing Runner: Scrapes, processes, and generates briefings.",
        formatter_class=argparse.RawTextHelpFormatter # Nicer help text formatting
    )
    parser.add_argument(
        '--feed',
        type=str,
        default=config.DEFAULT_FEED_PROFILE, # Use default from base config
        help=f"Specify the feed profile name (e.g., brazil, tech). Default: '{config.DEFAULT_FEED_PROFILE}'."
    )
    parser.add_argument(
        '--rate-articles',
        dest='rate',
        action='store_true',
        help='Run only the article impact rating stage (requires processed articles).'
    )
    parser.add_argument(
        '--scrape-articles',
        dest='scrape',
        action='store_true',
        help='Run only the article scraping stage.'
    )
    parser.add_argument(
        '--process-articles',
        dest='process',
        action='store_true',
        help='Run only the article processing (summarize, embed) stage.'
    )
    parser.add_argument(
        '--generate-brief',
        dest='generate',
        action='store_true',
        help='Run only the brief generation (cluster, analyze, synthesize) stage.'
    )
    parser.add_argument(
        '--all',
        dest='run_all',
        action='store_true',
        help='Run all stages sequentially (scrape, process, generate).\nThis is the default behavior if no specific stage argument is given.'
    )
    parser.add_argument(
        '--prepare',
        dest='prepare',
        action='store_true',
        help='Run preparation stages only (scrape, process, rate) without generating brief.'
    )

    args = parser.parse_args()

    # --- Load Feed Specific Config ---
    feed_profile_name = args.feed
    feed_module_name = f"feeds.{feed_profile_name}"
    try:
        feed_config = importlib.import_module(feed_module_name)
        print(f"Loaded feed configuration: {feed_module_name}")
        # Optionally merge settings if feed configs override base config values
        # For now, we just need RSS_FEEDS from it
        rss_feeds = getattr(feed_config, 'RSS_FEEDS', [])
        if not rss_feeds:
             print(f"Warning: RSS_FEEDS list not found or empty in {feed_module_name}.py")
    except ImportError:
        print(f"ERROR: Could not import feed configuration '{feed_module_name}.py'.")
        print(f"Please ensure the file exists and contains an RSS_FEEDS list.")
        # Decide how to handle: exit or continue without scraping/generation?
        # Let's allow processing/rating to run, but disable scrape/generate
        rss_feeds = None # Indicate feed load failure

    # --- Create Effective Config ---
    # Start with base config vars
    effective_config_dict = {k: v for k, v in config.__dict__.items() if not k.startswith('__')}
    # Override with feed_config vars if they exist
    if feed_config:
        for k, v in feed_config.__dict__.items():
            if not k.startswith('__'):
                effective_config_dict[k] = v

    # Convert dict to a simple object for easier access (optional)
    class EffectiveConfig:
        def __init__(self, dictionary):
            for k, v in dictionary.items():
                setattr(self, k, v)
    effective_config = EffectiveConfig(effective_config_dict)

    # Ensure RSS_FEEDS is correctly set in the effective config if loaded
    if rss_feeds is not None:
        effective_config.RSS_FEEDS = rss_feeds

    # Default to running all if no specific stage OR --all is provided
    should_run_all = args.run_all or not (args.scrape or args.process or args.generate or args.rate)

    # Apenas scrapping e processamento
    should_prepare = args.prepare

    print(f"\nMeridian Briefing Run [{feed_profile_name}] - {datetime.now()}")
    print("Initializing database...")
    database.init_db() # Initialize DB regardless of stage run

    current_rss_feeds = getattr(effective_config, 'RSS_FEEDS', None)

    if should_run_all:
        print("\n>>> Running ALL stages (including brief generation) <<<")
        if current_rss_feeds: 
            scrape_articles(feed_profile_name, current_rss_feeds, effective_config)
        else: 
            print("Skipping scrape stage: No RSS_FEEDS found for profile.")

        process_articles(feed_profile_name, effective_config)
        rate_articles(feed_profile_name, effective_config)

        if current_rss_feeds: 
            generate_brief(feed_profile_name, effective_config)
        else: 
            print("Skipping generate stage: No RSS_FEEDS found for profile.")
            
    elif should_prepare:
        print("\n>>> Running PREPARATION stages only (scrape, process, rate) - NO brief generation <<<")
        if current_rss_feeds:
            scrape_articles(feed_profile_name, current_rss_feeds, effective_config)
        else:
            print("Skipping scrape stage: No RSS_FEEDS found for profile.")

        process_articles(feed_profile_name, effective_config)
        rate_articles(feed_profile_name, effective_config)
        print("Preparation complete. Articles ready for briefing.")
        
    else:
        if args.scrape:
            if current_rss_feeds:
                print(f"\n>>> Running ONLY Scrape Articles stage [{feed_profile_name}] <<<")
                scrape_articles(feed_profile_name, current_rss_feeds, effective_config)
            else: 
                print(f"Cannot run scrape stage: No RSS_FEEDS found for profile '{feed_profile_name}'.")
        if args.process:
            print("\n>>> Running ONLY Process Articles stage <<<")
            process_articles(feed_profile_name, effective_config)
        if args.rate:
            print("\n>>> Running ONLY Rate Articles stage <<<")
            rate_articles(feed_profile_name, effective_config)
        if args.generate:
            if current_rss_feeds:
                print(f"\n>>> Running ONLY Generate Brief stage [{feed_profile_name}] <<<")
                generate_brief(feed_profile_name, effective_config)
            else: 
                print(f"Cannot run generate stage: No RSS_FEEDS found for profile '{feed_profile_name}'.")

    print(f"\nRun Finished [{feed_profile_name}] - {datetime.now()}")
