// src/components/TrendingSection.tsx
import { useEffect, useState, useRef } from 'react';
import type { Article, Feed } from '../types';
import { getFeeds, getTrendingArticles } from '../services/api';
import ArticleCard from './ArticleCard';
import SkeletonArticleCard from './SkeletonArticleCard';

interface TrendingSectionProps {
  title?: string;           // Título customizável
  feedProfile?: string;     // Filtrar por feed específico
  limit?: number;           // Quantos artigos mostrar
}

function TrendingSection({ 
  title = "Principais Notícias",
  feedProfile,
  limit = 10
}: TrendingSectionProps) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  
  // Referência para o container de scroll
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchTrending() {
      try {
        setLoading(true);

        const data = await getTrendingArticles(limit, feedProfile);
        setArticles(data);
        
      } catch (err) {
        console.error('Erro ao buscar trending:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchTrending();
  }, [feedProfile, limit]);

  useEffect(() => {
    getFeeds().then(setFeeds).catch(console.error);
  }, []);

  const feedsByName = Object.fromEntries(
    feeds.map(feed => [feed.name, feed])
  );

  // Verifica se pode rolar para os lados
  const checkScroll = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    setCanScrollLeft(container.scrollLeft > 0);
    setCanScrollRight(
      container.scrollLeft < container.scrollWidth - container.clientWidth
    );
  };

  // Rola para a esquerda
  const scrollLeft = () => {
    const container = scrollContainerRef.current;
    if (!container) return;
    
    container.scrollBy({
      left: -350, // Rola aproximadamente a largura de 1 card
      behavior: 'smooth'
    });
  };

  // Rola para a direita
  const scrollRight = () => {
    const container = scrollContainerRef.current;
    if (!container) return;
    
    container.scrollBy({
      left: 350, // Rola aproximadamente a largura de 1 card
      behavior: 'smooth'
    });
  };

  // Verifica scroll quando os artigos carregam
  useEffect(() => {
    if (articles.length > 0) {
      // Pequeno delay para garantir que o DOM foi renderizado
      setTimeout(checkScroll, 100);
    }
  }, [articles]);

  return (
    <div className="my-12">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">
            <b>{title}</b>
        </h2>

        {/* Container com scroll horizontal */}
        <div className="relative group">
            {/* Container de scroll */}
            <div 
                ref={scrollContainerRef}
                onScroll={checkScroll}
                className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide scroll-smooth"
            >
              {loading ? (
                [1, 2, 3, 4].map((i) => (
                  <SkeletonArticleCard key={i} />
                ))
              ) : (
                // Artigos reais
                articles.map((article) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    feedMeta={feedsByName[article.feed_profile]}
                  />
                ))
              )}
            </div>

            {/* Seta Esquerda */}
            {!loading && canScrollLeft && (
                <button
                    onClick={scrollLeft}
                    className="
                        absolute left-2 top-1/2 -translate-y-1/2
                        bg-white/95 hover:bg-white
                        text-gray-800 p-3 rounded-full shadow-lg
                        transition-all duration-300
                        opacity-0 group-hover:opacity-100
                        z-10
                    "
                    aria-label="Rolar para esquerda"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
            )}

            {/* Seta Direita */}
            {!loading && canScrollRight && (
                <button
                    onClick={scrollRight}
                    className="
                        absolute right-2 top-1/2 -translate-y-1/2
                        bg-white/95 hover:bg-white
                        text-gray-800 p-3 rounded-full shadow-lg
                        transition-all duration-300
                        opacity-0 group-hover:opacity-100
                        z-10
                    "
                    aria-label="Rolar para direita"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </button>
            )}

            {/* Gradiente fade na direita */}
            {!loading && canScrollRight && (
                <div className="absolute top-0 right-0 h-full w-20 bg-gradient-to-l from-gray-50 to-transparent pointer-events-none" />
            )}

            {/* Gradiente fade na esquerda */}
            {!loading && canScrollLeft && (
                <div className="absolute top-0 left-0 h-full w-20 bg-gradient-to-r from-gray-50 to-transparent pointer-events-none" />
            )}
        </div>
    </div>
  );
}

export default TrendingSection;