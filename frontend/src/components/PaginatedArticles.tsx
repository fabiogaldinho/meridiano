// src/components/PaginatedArticles.tsx
import { useEffect, useState } from 'react';
import type { Article, Feed } from '../types';
import ArticleCard from './ArticleCard';
import SkeletonArticleCard from './SkeletonArticleCard';
import { getFeeds } from '../services/api';

interface PaginatedArticlesProps {
  feedProfile?: string;     // Filtrar por feed específico
  title?: string;           // Título da seção
}

function PaginatedArticles({ 
  feedProfile,
  title = "Todos os Artigos"
}: PaginatedArticlesProps) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const perPage = 12;
  const [feeds, setFeeds] = useState<Feed[]>([]);

  useEffect(() => {
    async function fetchArticles() {
      try {
        setLoading(true);
        
        // Monta URL com filtros
        const params = new URLSearchParams({
          page: page.toString(),
          per_page: perPage.toString(),
          sort_by: 'published_date',
          direction: 'desc'
        });
        
        if (feedProfile) {
          params.append('feed_profile', feedProfile);
        }
        
        const response = await fetch(`/api/articles?${params}`);
        const data = await response.json();
        
        setArticles(data.articles);
        setTotalPages(data.total_pages);
      } catch (err) {
        console.error('Erro ao buscar artigos:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchArticles();
  }, [feedProfile, page]);
  
  useEffect(() => {
    getFeeds().then(setFeeds).catch(console.error);
  }, []);

  const feedsByName = Object.fromEntries(
    feeds.map(feed => [feed.name, feed])
  );

  return (
    <div className="my-12">
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6"><b>{title}</b></h2>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <SkeletonArticleCard key={i} />
          ))}
        </div>
      ) : articles.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400">Nenhum artigo encontrado.</p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                feedMeta={feedsByName[article.feed_profile]}
                variant="grid"
              />
            ))}
          </div>

          {/* Paginação */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className={`
                  px-4 py-2 rounded-lg font-semibold transition
                  ${page === 1 
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700'}
                `}
              >
                ← Anterior
              </button>

              <span className="text-gray-700 dark:text-gray-300 font-medium">
                Página {page} de {totalPages}
              </span>

              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className={`
                  px-4 py-2 rounded-lg font-semibold transition
                  ${page === totalPages 
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700'}
                `}
              >
                Próxima →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default PaginatedArticles;