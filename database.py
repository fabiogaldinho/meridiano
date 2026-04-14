"""
Database operations using SQLModel for the Meridiano application.
This replaces the SQLite-based database.py with modern SQLModel operations.
"""

import json, logging
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import and_, asc, desc, func, or_, select
from sqlalchemy import text

import config_base as config
from models import Article, Brief, Newsletter
from db import get_db_connection

logger = logging.getLogger(__name__)

ARTICLES_PER_PAGE_DEFAULT = 25

def get_unrated_articles(
    feed_profile: str, limit: int = 50
) -> List[Dict[str, Any]]:
    """Gets processed articles that haven't been rated yet."""
    with get_db_connection() as session:
        statement = (
            select(Article)
            .where(
                and_(
                    Article.processed_content.is_not(None), # type: ignore
                    Article.processed_content != "",
                    Article.processed_at.is_not(None), # type: ignore
                    Article.impact_score.is_(None), # type: ignore
                    Article.feed_profile == feed_profile,
                )
            )
            .order_by(desc(Article.processed_at))
            .limit(limit)
        )

        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def update_article_rating(article_id: int, impact_score: int) -> None:
    """Updates an article with its impact score."""
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            article.impact_score = impact_score
            session.add(article)
            session.commit()


def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves all data for a specific article by its ID."""
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        return _article_to_dict(article) if article else None


def _article_to_dict(article: Article) -> Dict[str, Any]:
    """Convert Article model to dictionary for compatibility with existing code."""
    if not article:
        return None

    return article.model_dump(
        include={
            "id",
            "url",
            "title",
            "published_date",
            "feed_source",
            "fetched_at",
            "raw_content",
            "formatted_content",
            "processed_content",
            "embedding",
            "processed_at",
            "cluster_id",
            "impact_score",
            "image_url",
            "feed_profile",
            "brief_ids",
            "initial_filter_score",
            "briefing_analyzed",
            "url_encoding",
            "marreta",
            "rss_description"
        }
    )


def _brief_to_dict(brief: Brief) -> Dict[str, Any]:
    """Convert Brief model to dictionary for compatibility with existing code."""
    if not brief:
        return None

    return brief.model_dump(
        include={
            "id",
            "generated_at",
            "brief_markdown",
            "contributing_article_ids",
            "feed_profile",
        }
    )

def _build_article_filters(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    feed_profile: Optional[str] = None,
    only_processed: bool = False
):
    """Helper for building filter conditions for articles."""
    filters = []

    if start_date:
        filters.append(func.date(Article.published_date) >= func.date(start_date))
    if end_date:
        filters.append(func.date(Article.published_date) <= func.date(end_date))
    if feed_profile:
        filters.append(Article.feed_profile == feed_profile)
    
    if only_processed:
        filters.append(Article.processed_at.is_not(None)) # type: ignore
        filters.append(Article.embedding.is_not(None)) # type: ignore
        filters.append(Article.impact_score.is_not(None)) # type: ignore
    
    filters.append(
            or_(
                Article.initial_filter_score.is_(None), # type: ignore
                Article.initial_filter_score >= 3 # type: ignore
            )
        )


    return filters


def get_all_articles(
    page: int = 1,
    per_page: int = ARTICLES_PER_PAGE_DEFAULT,
    sort_by: str = "published_date",
    direction: str = "desc",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    feed_profile: Optional[str] = None,
    search_term: Optional[str] = None,
    only_processed: bool = True,
    secondary_sort: str = None, # type: ignore
    secondary_direction: str = "desc",
    min_impact_score: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetches articles with filtering, sorting, and full-text search.
    Uses PostgreSQL full-text search when available, falls back to LIKE search.
    """
    with get_db_connection() as session:
        # Start with base query
        statement = select(Article)

        # Apply basic filters
        filters = _build_article_filters(start_date, end_date, feed_profile, only_processed)

        # Adiciona filtro de impact_score se fornecido
        if min_impact_score is not None:
            filters.append(Article.impact_score >= min_impact_score) # type: ignore

        if filters:
            statement = statement.where(and_(*filters))

        # Apply search if provided
        if search_term:
            if "postgresql" in config.DATABASE_URL.lower():
                # PostgreSQL full-text search
                search_vector = func.to_tsvector(
                    "english",
                    func.coalesce(Article.title, "")
                    + " "
                    + func.coalesce(Article.raw_content, ""),
                )
                # Use SQLAlchemy's match with a plain string and specify the Postgres
                # text search configuration to avoid nesting plainto_tsquery calls.
                statement = statement.where(
                    search_vector.match(search_term, postgresql_regconfig='english')
                )
            else:
                # Fallback to LIKE search for SQLite
                search_filter = or_(
                    Article.title.ilike(f"%{search_term}%"), # type: ignore
                    Article.raw_content.ilike(f"%{search_term}%"), # type: ignore
                )
                statement = statement.where(search_filter)

        # Apply sorting
        sort_columns = {
            "published_date": Article.published_date,
            "impact_score": Article.impact_score,
            "fetched_at": Article.fetched_at,
            "processed_at": Article.processed_at,
        }

        sort_column = sort_columns.get(sort_by, Article.published_date)

        if secondary_sort and secondary_sort in sort_columns:
            secondary_column = sort_columns[secondary_sort]


            if direction.lower() == "asc":
                if secondary_direction.lower() == "asc":
                    statement = statement.order_by(
                        asc(sort_column), 
                        asc(secondary_column), 
                        desc(Article.id)
                    )
                else:
                    statement = statement.order_by(
                        asc(sort_column), 
                        desc(secondary_column), 
                        desc(Article.id)
                    )
            else:
                if secondary_direction.lower() == "asc":
                    statement = statement.order_by(
                        desc(sort_column), 
                        asc(secondary_column), 
                        desc(Article.id)
                    )
                else:
                    statement = statement.order_by(
                        desc(sort_column), 
                        desc(secondary_column), 
                        desc(Article.id)
                    )
        else:
            if direction.lower() == "asc":
                statement = statement.order_by(asc(sort_column), desc(Article.id))
            else:
                statement = statement.order_by(desc(sort_column), desc(Article.id))

        # Apply pagination
        offset = (page - 1) * per_page
        statement = statement.offset(offset).limit(per_page)

        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def get_total_article_count(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    feed_profile: Optional[str] = None,
    search_term: Optional[str] = None,
    only_processed: bool = True
) -> int:
    """Returns total count of articles with optional filtering and search."""
    with get_db_connection() as session:
        # Start with base query
        statement = select(func.count(Article.id)) # type: ignore

        # Apply basic filters
        filters = _build_article_filters(start_date, end_date, feed_profile, only_processed)
        if filters:
            statement = statement.where(and_(*filters))

        # Apply search if provided
        if search_term:
            if "postgresql" in config.DATABASE_URL.lower():
                # PostgreSQL full-text search
                search_vector = func.to_tsvector(
                    "english",
                    func.coalesce(Article.title, "")
                    + " "
                    + func.coalesce(Article.raw_content, ""),
                )
                # Use SQLAlchemy's match with a plain string and specify the Postgres
                # text search configuration to avoid nesting plainto_tsquery calls.
                statement = statement.where(
                    search_vector.match(search_term, postgresql_regconfig='english')
                )
            else:
                # Fallback to LIKE search
                search_filter = or_(
                    Article.title.ilike(f"%{search_term}%"), # type: ignore
                    Article.raw_content.ilike(f"%{search_term}%"), # type: ignore
                )
                statement = statement.where(search_filter)

        return session.exec(statement).one()


def add_article(
    url: str,
    title: str,
    published_date: datetime,
    feed_source: str,
    raw_content: str,
    feed_profile: str,
    url_encoding: str,
    image_url: Optional[str] = None,
    initial_filter_score: Optional[int] = None,
    marreta: bool = False,
    briefing_analyzed: bool = False,
    formatted_content: Optional[str] = None,
    rss_description: Optional[str] = None
) -> Optional[int]:
    """Adds a new article with optional image URL."""
    with get_db_connection() as session:
        try:
            # Ensure Postgres sequence is in sync to avoid duplicate primary key errors
            if "postgresql" in config.DATABASE_URL.lower():
                try:
                    # Sync the sequence to the current max(id) so nextval() will produce a fresh value.
                    session.exec(                                                                                                       # type: ignore
                        text(                                                                                                           # type: ignore
                            "SELECT setval(pg_get_serial_sequence('articles','id'), COALESCE((SELECT MAX(id) FROM articles), 1))"
                        )
                    )
                except Exception as e:
                    # Log warning but continue - this is usually non-critical for new inserts
                    logger.warning(f"PostgreSQL sequence sync warning (non-critical): {e}")
                    # Continue - this is usually fine for new inserts

            article = Article(
                url=url,
                title=title,
                published_date=published_date,
                feed_source=feed_source,
                raw_content=raw_content,
                formatted_content=formatted_content,
                image_url=image_url,
                feed_profile=feed_profile,
                fetched_at=datetime.now(),
                initial_filter_score=initial_filter_score,
                url_encoding=url_encoding,
                marreta=marreta,
                briefing_analyzed=briefing_analyzed,
                rss_description=rss_description
            )
            session.add(article)
            session.commit()
            session.refresh(article)  # Get the ID
            print(f"Added article [{feed_profile}]: {title}")
            return article.id
        except IntegrityError:
            session.rollback()
            return None


def get_unprocessed_articles(
    feed_profile: str, limit: int = 50
) -> List[Dict[str, Any]]:
    """Gets articles that haven't been processed yet."""
    with get_db_connection() as session:
        statement = (
            select(Article)
            .where(
                and_(
                    Article.processed_at.is_(None),                                 # type: ignore
                    Article.raw_content.is_not(None),                               # type: ignore
                    Article.raw_content != "",
                    Article.feed_profile == feed_profile,
                    or_(
                        Article.initial_filter_score.is_(None),                                 # type: ignore
                        Article.initial_filter_score >= 3                                       # type: ignore
                    )
                )
            )
            .order_by(desc(Article.fetched_at))
            .limit(limit)
        )

        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def get_articles_pending_filter(feed_profile: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Busca artigos que ainda não passaram pelo filtro inicial (initial_filter_score=NULL).
    """
    with get_db_connection() as session:
        statement = select(Article).where(
            Article.initial_filter_score.is_(None)  # type: ignore
        )
        
        if feed_profile:
            statement = statement.where(Article.feed_profile == feed_profile)
        
        statement = statement.order_by(desc(Article.published_date)).limit(limit)
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def update_article_processing(
    article_id: int, processed_content: str, embedding: Optional[List[float]]
) -> None:
    """Updates an article with its summary, embedding, and processed timestamp."""
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            article.processed_content = processed_content
            article.embedding = json.dumps(embedding) if embedding else None
            article.processed_at = datetime.now()
            session.add(article)
            session.commit()


def get_articles_for_briefing(
    feed_profile: str,
    min_impact_score: int = 5
) -> List[Dict[str, Any]]:
    """
    Gets articles that are ready for briefing but haven't been analyzed yet.
    
    Args:
        feed_profile: Which feed profile to get articles for
        min_impact_score: Minimum impact score to consider (default 5)
    
    Returns:
        List of article dictionaries ready for briefing
    """
    with get_db_connection() as session:
        statement = (
            select(Article)
            .where(
                and_(
                    Article.feed_profile == feed_profile,
                    Article.processed_at.is_not(None),                                 # type: ignore
                    Article.embedding.is_not(None),                                    # type: ignore
                    Article.impact_score.is_not(None),                                 # type: ignore
                    Article.impact_score >= min_impact_score,                          # type: ignore
                    Article.briefing_analyzed == False
                )
            )
            .order_by(desc(Article.impact_score), desc(Article.processed_at))
        )

        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def save_brief(
    brief_markdown: str, contributing_article_ids: List[int], feed_profile: str
) -> int:
    """Saves the generated brief including its feed profile."""
    with get_db_connection() as session:
        ids_json = json.dumps(contributing_article_ids)
        brief = Brief(
            brief_markdown=brief_markdown,
            contributing_article_ids=ids_json,
            feed_profile=feed_profile,
            generated_at=datetime.now(),
        )

        # Guarantee unique and sequential id
        if "postgresql" in config.DATABASE_URL.lower():
            try:
                session.exec(                                                                                                                # type: ignore
                    text(                                                                                                                    # type: ignore
                        "SELECT setval(pg_get_serial_sequence('briefs','id'), COALESCE((SELECT MAX(id) FROM briefs), 1))"
                    )
                )
            except Exception:
                pass

        session.add(brief)
        session.commit()
        session.refresh(brief)  # Get the ID
        print(f"Saved brief [{feed_profile}] with ID: {brief.id}")


        # Atualizar cada artigo usado
        for article_id in contributing_article_ids:
            statement = select(Article).where(Article.id == article_id)
            article = session.exec(statement).first()

            if article:
                current_brief_ids = []
                if article.brief_ids:
                    try:
                        current_brief_ids = json.loads(article.brief_ids)
                    except json.JSONDecodeError:
                        current_brief_ids = []
                
                if brief.id not in current_brief_ids:
                    current_brief_ids.append(brief.id)
                    
                    article.brief_ids = json.dumps(current_brief_ids)
                    session.add(article)

        session.commit()


        return brief.id                                 # type: ignore


def get_all_briefs_metadata(
    feed_profile: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieves ID, timestamp, and profile for briefs, newest first, optionally filtered."""
    with get_db_connection() as session:
        statement = select(Brief)

        if feed_profile:
            statement = statement.where(Brief.feed_profile == feed_profile)

        statement = statement.order_by(desc(Brief.generated_at))
        briefs = session.exec(statement).all()

        return [_brief_to_dict(brief) for brief in briefs]


def get_brief_by_id(brief_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a specific brief's content and timestamp by its ID."""
    with get_db_connection() as session:
        statement = select(Brief).where(Brief.id == brief_id)
        brief = session.exec(statement).first()
        return _brief_to_dict(brief) if brief else None


def get_distinct_feed_profiles(table: str = "articles") -> List[str]:
    """Gets a list of distinct feed_profile values from a table."""
    if table not in ["articles", "briefs"]:
        raise ValueError("Invalid table name for distinct profiles.")

    with get_db_connection() as session:
        if table == "articles":
            statement = (
                select(Article.feed_profile)
                .distinct()
                .order_by(Article.feed_profile)
            )
            result = session.exec(statement).all()
        else:  # table == 'briefs'
            statement = (
                select(Brief.feed_profile)
                .distinct()
                .order_by(Brief.feed_profile)
            )
            result = session.exec(statement).all()

        return list(result)


def update_article_filter_score(article_id: int, score: int) -> None:
    """Atualiza o initial_filter_score de um artigo."""
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            article.initial_filter_score = score
            session.add(article)
            session.commit()


def get_approved_articles_without_content(feed_profile: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    """
    Busca artigos aprovados no filtro (score >= 3) mas sem raw_content.
    """
    with get_db_connection() as session:
        statement = select(Article).where(
            and_(
                Article.initial_filter_score >= 3,          # type: ignore
                or_(
                    Article.raw_content.is_(None),          # type: ignore
                    Article.raw_content == ""
                )
            )
        )
        
        if feed_profile:
            statement = statement.where(Article.feed_profile == feed_profile)
        
        statement = statement.order_by(desc(Article.published_date)).limit(limit)
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def update_article_content(
    article_id: int,
    raw_content: str,
    image_url: Optional[str] = None,
    marreta: bool = False
) -> None:
    """
    Atualiza um artigo com o conteúdo extraído.
    """
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            article.raw_content = raw_content
            article.image_url = image_url
            article.marreta = marreta
            session.add(article)
            session.commit()


def get_articles_pending_summary(
    feed_profile: str = None, limit: int = 500
) -> List[Dict[str, Any]]:
    """Gets articles with content but not yet summarized."""
    with get_db_connection() as session:
        filters = [
            Article.raw_content.is_not(None),
            Article.raw_content != "",
            Article.processed_content.is_(None),
            or_(
                Article.initial_filter_score.is_(None),
                Article.initial_filter_score >= 3
            )
        ]
        
        if feed_profile:
            filters.append(Article.feed_profile == feed_profile)
        
        statement = (
            select(Article)
            .where(and_(*filters))
            .order_by(desc(Article.fetched_at))
            .limit(limit)
        )
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def get_articles_pending_embedding(
    feed_profile: str = None, limit: int = 500
) -> List[Dict[str, Any]]:
    """Gets articles with summary but not yet embedded."""
    with get_db_connection() as session:
        filters = [
            Article.processed_content.is_not(None),
            Article.processed_content != "",
            Article.embedding.is_(None),
            or_(
                Article.initial_filter_score.is_(None),
                Article.initial_filter_score >= 3
            )
        ]
        
        if feed_profile:
            filters.append(Article.feed_profile == feed_profile)
        
        statement = (
            select(Article)
            .where(and_(*filters))
            .order_by(desc(Article.processed_at))
            .limit(limit)
        )
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]
    

def update_article_embedding(article_id: int, embedding: List[float]) -> None:
    """Updates an article with its embedding vector."""
    with get_db_connection() as session:
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            article.embedding = json.dumps(embedding)
            session.add(article)
            session.commit()


def get_articles_pending_rating(
    feed_profile: str = None, limit: int = 500
) -> List[Dict[str, Any]]:
    """Gets articles with embedding but not yet rated."""
    with get_db_connection() as session:
        filters = [
            Article.processed_content.is_not(None),
            Article.embedding.is_not(None),
            Article.impact_score.is_(None),
            or_(
                Article.initial_filter_score.is_(None),
                Article.initial_filter_score >= 3
            )
        ]
        
        if feed_profile:
            filters.append(Article.feed_profile == feed_profile)
        
        statement = (
            select(Article)
            .where(and_(*filters))
            .order_by(desc(Article.processed_at))
            .limit(limit)
        )
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def get_articles_for_newsletter(
    feed_profile: str,
    min_score: int,
    days_back: int = 3,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Busca artigos elegíveis para newsletter.
    
    Critérios:
    - feed_profile específico
    - published_date nos últimos X dias
    - impact_score >= min_score
    - newsletter_ids IS NULL (nunca usado em newsletter)
    - Ordenado por impact_score DESC
    - Limitado a top N
    """
    from datetime import timedelta
    
    with get_db_connection() as session:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        statement = (
            select(Article)
            .where(
                and_(
                    Article.feed_profile == feed_profile,
                    Article.published_date >= cutoff_date,
                    Article.impact_score >= min_score,
                    Article.newsletter_ids.is_(None),
                    Article.newsletter_deduplicated_at.is_(None)
                )
            )
            .order_by(desc(Article.impact_score), desc(Article.published_date))
            .limit(limit)
        )
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]

def save_newsletter(
    newsletter_markdown: str,
    contributing_article_ids: List[int],
    feed_profile: str,
    featured_image: str
) -> int:
    """Salva a newsletter gerada e atualiza os artigos incluídos."""
    with get_db_connection() as session:
        from models import Newsletter
        
        ids_json = json.dumps(contributing_article_ids)
        newsletter = Newsletter(
            newsletter_markdown=newsletter_markdown,
            contributing_article_ids=ids_json,
            feed_profile=feed_profile,
            generated_at=datetime.now(),
            featured_image=featured_image
        )
        
        session.add(newsletter)
        session.commit()
        session.refresh(newsletter)
        
        print(f"Saved newsletter [{feed_profile}] with ID: {newsletter.id}")
        
        # Atualizar cada artigo com o newsletter_id
        for article_id in contributing_article_ids:
            statement = select(Article).where(Article.id == article_id)
            article = session.exec(statement).first()
            
            if article:
                current_ids = []
                if article.newsletter_ids:
                    try:
                        current_ids = json.loads(article.newsletter_ids)
                    except json.JSONDecodeError:
                        current_ids = []
                
                if newsletter.id not in current_ids:
                    current_ids.append(newsletter.id)
                    article.newsletter_ids = json.dumps(current_ids)
                    session.add(article)
        
        session.commit()
        
        return newsletter.id


def _newsletter_to_dict(newsletter: Newsletter) -> Dict[str, Any]:
    """Convert Newsletter model to dictionary."""
    if not newsletter:
        return None
    
    return newsletter.model_dump(
        include={
            "id",
            "generated_at",
            "feed_profile",
            "newsletter_markdown",
            "contributing_article_ids",
            "featured_image"
        }
    )


def get_all_newsletters(
    feed_profile: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Busca newsletters, opcionalmente filtradas por feed_profile."""
    with get_db_connection() as session:
        statement = select(Newsletter)
        
        if feed_profile:
            statement = statement.where(Newsletter.feed_profile == feed_profile)
        
        statement = statement.order_by(desc(Newsletter.generated_at)).limit(limit)
        
        newsletters = session.exec(statement).all()
        return [_newsletter_to_dict(n) for n in newsletters]


def get_newsletter_by_id(newsletter_id: int) -> Optional[Dict[str, Any]]:
    """Busca uma newsletter específica por ID."""
    with get_db_connection() as session:
        statement = select(Newsletter).where(Newsletter.id == newsletter_id)
        newsletter = session.exec(statement).first()
        return _newsletter_to_dict(newsletter) if newsletter else None


def get_articles_for_weekly_briefing(
    feed_profile: str,
    min_impact_score: int = 8
) -> List[Dict[str, Any]]:
    """
    Busca artigos para o briefing semanal.
    
    Período: último sábado - 7 dias (sábado anterior) até último sábado - 1 dia (sexta).
    
    Critérios:
    - feed_profile específico
    - published_date no período da semana
    - impact_score >= min_impact_score
    - briefing_analyzed == False
    - embedding IS NOT NULL
    """
    hoje = datetime.now().date()
    dias_ate_ultimo_sabado = (hoje.weekday() - 5) % 7
    ultimo_sabado = hoje - timedelta(days=dias_ate_ultimo_sabado)
    
    start_date = ultimo_sabado - timedelta(days=7)  # sábado anterior
    end_date = ultimo_sabado - timedelta(days=1)    # sexta-feira
    
    with get_db_connection() as session:
        statement = (
            select(Article)
            .where(
                and_(
                    Article.feed_profile == feed_profile,
                    func.date(Article.published_date) >= start_date,
                    func.date(Article.published_date) <= end_date,
                    Article.impact_score >= min_impact_score,
                    Article.briefing_analyzed == False,
                    Article.embedding.is_not(None)
                )
            )
            .order_by(desc(Article.impact_score), desc(Article.published_date))
        )
        
        articles = session.exec(statement).all()
        return [_article_to_dict(article) for article in articles]


def mark_articles_newsletter_deduplicated(article_ids: List[int]) -> int:
    """
    Marca artigos como excluídos por deduplicação na newsletter.
    """
    if not article_ids:
        return 0
    
    with get_db_connection() as session:
        count = 0
        for article_id in article_ids:
            statement = select(Article).where(Article.id == article_id)
            article = session.exec(statement).first()
            
            if article:
                article.newsletter_deduplicated_at = datetime.now()
                session.add(article)
                count += 1
        
        session.commit()
        logger.info(f"Marcados {count} artigos como deduplicados para newsletter")



def init_db() -> None:
    from db import create_db_and_tables
    create_db_and_tables()