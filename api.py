# meridiano/api.py
from flask import Blueprint, jsonify, request
import database, math, importlib, json


api_bp = Blueprint('api', __name__, url_prefix='/api')

def extract_preview_without_title(markdown_text, max_chars=200):
    """
    Remove o primeiro título (## ou ###) e pega o primeiro parágrafo.
    """
    lines = markdown_text.split('\n')
    
    clean_lines = []
    skip_first_title = True
    
    for line in lines:
        line = line.strip()
        
        if skip_first_title and line.startswith('#'):
            skip_first_title = False
            continue
        
        if line:
            clean_lines.append(line)
    
    preview_text = ' '.join(clean_lines)
    
    if len(preview_text) > max_chars:
        return preview_text[:max_chars] + '...'
    
    return preview_text


@api_bp.route('/briefings', methods=['GET'])
def get_briefings():
    """
    Retorna lista de briefings com preview e imagem destacada.
    """
    feed_profile = request.args.get('feed_profile', None)
    limit = min(int(request.args.get('limit', 20)), 100)
    
    briefs = database.get_all_briefs_metadata(
        feed_profile=feed_profile if feed_profile else None
    )
    
    briefs = briefs[:limit]
    
    briefs_summary = []
    for brief in briefs:
        article_ids = []
        if brief.get('contributing_article_ids'):
            try:
                article_ids = json.loads(brief['contributing_article_ids'])
            except:
                article_ids = []
        

        featured_image = None
        if article_ids:
            from sqlmodel import select, desc, and_
            from models import Article
            
            with database.get_db_connection() as session:
                stmt = (
                    select(Article)
                    .where(
                        and_(
                            Article.id.in_(article_ids),           # type: ignore
                            Article.image_url.is_not(None),         # type: ignore
                            Article.image_url != ''                 # type: ignore
                        )
                    )
                    .order_by(desc(Article.impact_score))
                    .limit(1)
                )
                
                featured_article = session.exec(stmt).first()
                
                if featured_article:
                    featured_image = featured_article.image_url
        
        briefs_summary.append({
            'id': brief['id'],
            'generated_at': brief['generated_at'],
            'feed_profile': brief['feed_profile'],
            'preview': extract_preview_without_title(brief['brief_markdown'], 200),
            'featured_image': featured_image
        })
    
    return jsonify({
        'briefings': briefs_summary,
        'count': len(briefs_summary)
    })


@api_bp.route('/briefings/<int:brief_id>', methods=['GET'])
def get_briefing(brief_id):
    """
    Retorna um briefing específico pelo ID.
    
    Exemplo: GET /api/briefings/42
    """
    brief = database.get_brief_by_id(brief_id)
    
    if brief is None:
        return jsonify({'error': 'Briefing not found'}), 404
    
    featured_image = None
    article_ids = []
    
    if brief.get('contributing_article_ids'):
        try:
            article_ids = json.loads(brief['contributing_article_ids'])
        except:
            article_ids = []
    
    if article_ids:
        from sqlmodel import select, desc, and_
        from models import Article
        
        with database.get_db_connection() as session:
            stmt = (
                select(Article)
                .where(
                    and_(
                        Article.id.in_(article_ids),            # type: ignore
                        Article.image_url.is_not(None),         # type: ignore
                        Article.image_url != ''                 # type: ignore
                    )
                )
                .order_by(desc(Article.impact_score))
                .limit(1)
            )
            
            featured_article = session.exec(stmt).first()
            
            if featured_article:
                featured_image = featured_article.image_url
    
    return jsonify({
        'id': brief['id'],
        'generated_at': brief['generated_at'],
        'feed_profile': brief['feed_profile'],
        'brief_markdown': brief['brief_markdown'],
        'contributing_article_ids': brief['contributing_article_ids'],
        'featured_image': featured_image
    })


@api_bp.route('/articles', methods=['GET'])
def get_articles():
    """
    Retorna lista paginada de artigos.
    
    Query params opcionais:
    - page: número da página (default: 1)
    - per_page: artigos por página (default: 15)
    - feed_profile: filtrar por perfil
    - sort_by: ordenar por campo (published_date ou impact_score)
    - direction: asc ou desc
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))
    feed_profile = request.args.get('feed_profile', None)
    sort_by = request.args.get('sort_by', 'published_date')
    direction = request.args.get('direction', 'desc')
    
    articles = database.get_all_articles(
        page=page,
        per_page=per_page,
        feed_profile=feed_profile,
        sort_by=sort_by,
        direction=direction,
        only_processed=True
    )
    
    total_count = database.get_total_article_count(
        feed_profile=feed_profile,
        only_processed=True
    )
    
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 0
    
    return jsonify({
        'articles': articles,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })



@api_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    Retorna um artigo específico por ID.
    
    Exemplo: GET /api/articles/42
    """
    article = database.get_article_by_id(article_id)
    
    if article is None:
        return jsonify({'error': 'Article not found'}), 404
    
    return jsonify(article)


@api_bp.route('/articles/trending', methods=['GET'])
def get_trending_articles():
    """
    Retorna artigos com impact_score >= 8 (trending).
    
    Query params opcionais:
    - limit: número máximo de artigos (default: 10)
    """
    limit = int(request.args.get('limit', 10))
    feed_profile = request.args.get('feed_profile', None)
    
    articles = database.get_all_articles(
        page=1,
        per_page=limit,
        sort_by='processed_at',
        direction='desc',
        secondary_sort='impact_score',
        secondary_direction='desc',
        only_processed=True,
        min_impact_score=9,
        feed_profile=feed_profile
    )
    
    return jsonify({
        'articles': articles[:limit],
        'count': len(articles[:limit])
    })


@api_bp.route('/feeds', methods=['GET'])
def get_feeds():
    """
    Retorna lista de feeds (profiles) disponíveis com display_name.
    """
    # Pega lista de feeds do banco
    profiles = database.get_distinct_feed_profiles(table='articles')
    
    # Para cada profile, carrega o display_name do arquivo do feed
    feeds_list = []
    for profile in profiles:
        try:
            # Importa o módulo do feed dinamicamente
            feed_module = importlib.import_module(f'feeds.{profile}')
            
            # Pega DISPLAY_NAME com fallback
            display_name = getattr(
                feed_module,
                'DISPLAY_NAME',
                profile.replace('-', ' ').title()  # Fallback se não existir
            )

            # Pega TEXT_COLOR com fallback
            text_color = getattr(feed_module, 'TEXT_COLOR', 'text-gray-800')
            
            feeds_list.append({
                'name': profile,
                'display_name': display_name,
                'text_color': text_color
            })
        except ImportError:
            # Se o arquivo do feed não existir, usa nome formatado
            feeds_list.append({
                'name': profile,
                'display_name': profile.replace('-', ' ').title(),
                'text_color': 'text-gray-800'
            })
    
    return jsonify({
        'feeds': feeds_list,
        'count': len(feeds_list)
    })