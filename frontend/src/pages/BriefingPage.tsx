// src/pages/BriefingPage.tsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import type { Briefing, Article, Feed } from '../types';
import { getBriefing, getFeeds } from '../services/api';
import ArticleCard from '../components/ArticleCard';
import SkeletonBriefingPage from '../components/SkeletonBriefingPage';

function BriefingPage() {
  const { id } = useParams<{ id: string }>();
  
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    async function fetchData() {
      if (!id) return;

      try {
        setLoading(true);

        // Busca briefing e feeds em paralelo
        const [briefingData, feedsData] = await Promise.all([
          getBriefing(parseInt(id)),
          getFeeds()
        ]);

        setBriefing(briefingData);
        setFeeds(feedsData);

        // DEBUG: Ver o que está chegando
        console.log('Briefing completo:', briefingData);
        console.log('Featured image:', briefingData.featured_image);

        // Busca artigos relacionados
        const articleIds: number[] = JSON.parse(briefingData.contributing_article_ids || '[]');
        
        console.log('IDs dos artigos:', articleIds);

        const articlePromises = articleIds.map(async (articleId) => {
          const response = await fetch(`/api/articles/${articleId}`);
          return response.ok ? await response.json() : null;
        });

        const articlesData = await Promise.all(articlePromises);
        setArticles(articlesData.filter(a => a !== null));

        console.log('Artigos carregados:', articlesData.filter(a => a !== null).length);

      } catch (err) {
        console.error('Erro ao carregar briefing:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  // Loading state
  if (loading) {
    return <SkeletonBriefingPage />;
  }

  // Not found
  if (!briefing) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">❌</div>
          <p className="text-gray-600 mb-4">Briefing não encontrado</p>
          <Link to="/" className="text-blue-600 hover:underline">
            Voltar para Home
          </Link>
        </div>
      </div>
    );
  }

  // Helpers
  const feedsByName = Object.fromEntries(feeds.map(f => [f.name, f]));
  const feedMeta = feedsByName[briefing.feed_profile];
  
  const formattedDate = new Date(briefing.generated_at).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-600 mb-6">
        <Link to="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">/</span>
        <Link to={`/feeds/${briefing.feed_profile}`} className="hover:text-blue-600">
          {feedMeta?.display_name || briefing.feed_profile}
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-800">Briefing #{briefing.id}</span>
      </nav>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="flex items-center gap-3 mb-4">
          {/* Badge do feed */}
          <span 
            className={`inline-block bg-gray-100 px-4 py-2 rounded-full text-sm font-semibold uppercase ${feedMeta?.text_color || 'text-gray-800'}`}
          >
            {feedMeta?.display_name || briefing.feed_profile}
          </span>
          
          {/* Data */}
          <span className="text-gray-600 text-sm">
            {formattedDate}
          </span>
        </div>

        {/* Título */}
        <h1 className="text-4xl font-bold text-gray-800">
          Briefing #{briefing.id}
        </h1>
      </div>

      {/* Featured Image */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
        {!briefing.featured_image || imgError ? (
          // Gradiente quando não tem imagem
          <div className="w-full h-96 bg-gradient-to-br from-slate-800 via-gray-900 to-black flex items-center justify-center">
            <span className="text-white text-9xl opacity-20">📋</span>
            {/* DEBUG */}
            <div className="absolute bottom-4 left-4 text-white text-xs opacity-50">
              {!briefing.featured_image ? 'Sem imagem' : 'Erro ao carregar'}
            </div>
          </div>
        ) : (
          // Imagem quando existe
          <img 
            src={briefing.featured_image}
            alt={`Briefing #${briefing.id}`}
            className="w-full h-96 object-cover"
            onError={() => {
              console.error('Erro ao carregar imagem:', briefing.featured_image);
              setImgError(true);
            }}
            onLoad={() => console.log('Imagem carregada com sucesso!')}
          />
        )}
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="prose prose-lg max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-a:text-blue-600 prose-strong:text-gray-900">
          <ReactMarkdown rehypePlugins={[rehypeRaw]}>
            {briefing.brief_markdown}
          </ReactMarkdown>
        </div>
      </div>

      {/* Related Articles */}
      {articles.length > 0 && (
        <div className="mt-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">
            Artigos Relacionados ({articles.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                feedMeta={feedsByName[article.feed_profile]}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BriefingPage;