// src/components/ArticleCard.tsx
import type { Article, Feed } from '../types';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface ArticleCardProps {
  article: Article;
  feedMeta?: Feed;
  onClick?: () => void;
  variant?: 'scroll' | 'grid' | 'grid-compact';
}

function impactBadgeClass(score: number) {
  if (score >= 9) {
    return 'bg-gradient-to-r from-red-500/90 to-rose-500/90 text-white';
  }
  if (score >= 8) {
    return 'bg-gradient-to-r from-orange-400/90 to-amber-400/90 text-white';
  }
  if (score >= 6) {
    return 'bg-gradient-to-r from-yellow-300/90 to-yellow-400/90 text-gray-900';
  }
  if (score >= 4) {
    return 'bg-gradient-to-r from-emerald-300/90 to-green-400/90 text-gray-900';
  }
  return 'bg-gradient-to-r from-slate-200/90 to-slate-300/90 text-gray-800';
}


function ArticleCard({ article, feedMeta, onClick, variant = 'scroll' }: ArticleCardProps) {
  const formattedDate = new Date(article.published_date).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });

  const [imgError, setImgError] = useState(false);
  const navigate = useNavigate();

  // Se não passar onClick, usa navegação padrão
  const handleClick = onClick || (() => navigate(`/articles/${article.id}`));

    const handleFeedClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        navigate(`/feeds/${article.feed_profile}`);
    };

  const isCompact = variant === 'grid-compact';
  
  const imageHeight = isCompact ? 'h-28' : 'h-40';
  const contentPadding = isCompact ? 'p-3' : 'p-6';


  return (
    <div 
      onClick={handleClick}
      className={`
        bg-white rounded-xl shadow-md overflow-hidden 
        transition-all duration-300 cursor-pointer 
        hover:shadow-xl hover:-translate-y-1
        ${variant === 'scroll' ? 'flex-shrink-0 w-80' : 'w-full'}
      `}
    >
      {/* Imagem do artigo ou gradiente como placeholder */}
      <div className={`relative ${imageHeight} w-full`}>
        {!article.image_url || imgError ? (
          <div className="w-full h-full bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center">
            <span className="text-white text-6xl opacity-30">📰</span>
          </div>
        ) : (
          <img 
            src={article.image_url}
            alt={article.title}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        )}

        {/* Badges sobrepostos na imagem */}
        <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
            {/* Badge do feed profile (esquerda) */}
            {feedMeta && (
                <button
                onClick={handleFeedClick}
                className={`inline-block bg-white/90 backdrop-blur-sm rounded-md font-semibold uppercase ${feedMeta.text_color} hover:bg-white transition-colors ${isCompact ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'}`}
                >
                {feedMeta.display_name}
                </button>
            )}

          {/* Badge de impact score (direita) */}
          {article.impact_score && (
            <span className={`
              inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold
              backdrop-blur-sm shadow-sm
              ${impactBadgeClass(article.impact_score)}
            `}>
              🔥 {article.impact_score}
            </span>
          )}
        </div>
      </div>

      {/* Conteúdo do card */}
      <div className={contentPadding}>
        {/* Título do artigo */}
        <h3 className="text-lg font-bold text-gray-800 mb-2 line-clamp-2">
          {article.title}
        </h3>

        {/* Data */}
        <p className="text-gray-600 text-sm mb-3">
          {formattedDate}
        </p>

        {/* Resumo do artigo */}
        {article.processed_content && (
          <p className="text-gray-700 text-sm line-clamp-3 mb-3">
            {article.processed_content}
          </p>
        )}

        {/* Link "Ler mais" */}
        {onClick && (
          <p className="text-blue-600 font-semibold text-sm">
            Ler mais →
          </p>
        )}
      </div>
    </div>
  );
}

export default ArticleCard;