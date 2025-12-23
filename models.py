"""
SQLModel database models for Meridiano application.
"""

from datetime import datetime
from typing import Optional, ClassVar
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    """Article model representing news articles in the database."""

    # Old SQLite schema for reference
    """
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, /* id is alias for rowid */
        url TEXT UNIQUE NOT NULL,
        title TEXT,
        published_date DATETIME,
        feed_source TEXT,
        fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        raw_content TEXT,
        processed_content TEXT,
        embedding TEXT,
        processed_at DATETIME,
        cluster_id INTEGER,
        impact_score INTEGER,
        image_url TEXT,
        feed_profile TEXT NOT NULL DEFAULT 'default'
    );
    CREATE INDEX IF NOT EXISTS idx_articles_url ON articles (url);
    CREATE INDEX IF NOT EXISTS idx_articles_processed_at ON articles (processed_at);
    CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles (published_date);
    """

    __tablename__: ClassVar[str] = "articles"                                                           # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(unique=True, index=True)
    title: Optional[str] = None
    published_date: Optional[datetime] = None
    feed_source: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.now)
    raw_content: Optional[str] = None
    processed_content: Optional[str] = None
    embedding: Optional[str] = None  # JSON string
    processed_at: Optional[datetime] = Field(default=None, index=True)
    cluster_id: Optional[int] = None
    impact_score: Optional[int] = None
    image_url: Optional[str] = None
    feed_profile: str = Field(default="default", index=True)
    brief_ids: Optional[str] = Field(
        default=None,
        description="JSON array of brief IDs where this article was used"
    )
    initial_filter_score: Optional[int] = Field(
        default=None,
        description="Initial relevance score (1-5) from RSS snippet analysis"
    )
    briefing_analyzed: bool = Field(default=False, index=True)
    url_encoding: str = Field(unique=True, index=True)
    marreta: Optional[bool] = Field(default=False, index=True)


class Brief(SQLModel, table=True):
    """Brief model representing generated news briefs."""

    # Old SQLite schema for reference
    """
    # Briefs Table
    CREATE TABLE IF NOT EXISTS briefs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        brief_markdown TEXT NOT NULL,
        contributing_article_ids TEXT,
        feed_profile TEXT NOT NULL DEFAULT 'default'
    )
    """

    __tablename__: ClassVar[str] = "briefs"                                                 # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    generated_at: datetime = Field(default_factory=datetime.now)
    brief_markdown: str
    contributing_article_ids: Optional[str] = None  # JSON string
    feed_profile: str = Field(default="default", index=True)