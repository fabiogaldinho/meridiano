// src/components/RelatedArticles.tsx
import { useState, useRef, useEffect } from 'react';
import type { Article, Feed } from '../types';
import ArticleCard from './ArticleCard';

interface RelatedArticlesProps {
  articles: Article[];        // Array completo de artigos
  feeds: Feed[];              // Feeds para metadata
}

function RelatedArticles({ articles, feeds }: RelatedArticlesProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [isFirstRender, setIsFirstRender] = useState(true);
  const articlesPerPage = 12;
  const sectionRef = useRef<HTMLDivElement>(null);

  // Mapeia feeds por nome para lookup rápido
  const feedsByName = Object.fromEntries(
    feeds.map(feed => [feed.name, feed])
  );

  // Calcula total de páginas
  const totalPages = Math.ceil(articles.length / articlesPerPage);

  // Calcula índices para slice do array
  const startIndex = (currentPage - 1) * articlesPerPage;
  const endIndex = startIndex + articlesPerPage;
  
  // Artigos da página atual
  const currentArticles = articles.slice(startIndex, endIndex);

  // Função para ir para página anterior
  const goToPreviousPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  // Função para ir para próxima página
  const goToNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  // Scroll para topo da seção ao mudar de página
  useEffect(() => {
    // Marca que já passou do primeiro render
    if (isFirstRender) {
      setIsFirstRender(false);
      return;
    }

    // Scroll ao mudar de página
    if (sectionRef.current) {
      const elementPosition = sectionRef.current.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - 80;
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  }, [currentPage]);

  // Se não tem artigos, não renderiza nada
  if (articles.length === 0) {
    return null;
  }

  return (
    <div ref={sectionRef} className="mt-12">
      {/* Título */}
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6">
        <b>ARTIGOS RELACIONADOS</b>
      </h2>

      {/* Grid de Artigos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {currentArticles.map((article) => (
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
          {/* Botão Anterior */}
          <button
            onClick={goToPreviousPage}
            disabled={currentPage === 1}
            className={`
              px-4 py-2 rounded-lg font-semibold transition
              ${currentPage === 1 
                ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'}
            `}
          >
            ← Anterior
          </button>

          {/* Indicador de Página */}
          <span className="text-gray-700 dark:text-gray-300 font-medium">
            Página {currentPage} de {totalPages}
          </span>

          {/* Botão Próxima */}
          <button
            onClick={goToNextPage}
            disabled={currentPage === totalPages}
            className={`
              px-4 py-2 rounded-lg font-semibold transition
              ${currentPage === totalPages 
                ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'}
            `}
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  );
}

export default RelatedArticles;