// src/pages/BriefingPage.tsx
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import type { Briefing, Article, Feed } from '../types';
import { getBriefing, getFeeds, getArticle } from '../services/api';
import ArticleCard from '../components/ArticleCard';
import SkeletonBriefingPage from '../components/SkeletonBriefingPage';

function BriefingPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    
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

            const articlePromises = articleIds.map(articleId => getArticle(articleId));

        const articlesData = await Promise.all(articlePromises);
        setArticles(articlesData);

        console.log('Artigos carregados:', articlesData.length);

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
  
    const handleFeedClick = () => {
        navigate(`/feeds/${briefing.feed_profile}`);
    };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
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

      {/* Featured Image */}
      <div className="relative rounded-2xl overflow-hidden shadow-2xl mb-8 h-[400px]">
        {/* Background */}
        <div className="absolute inset-0 z-0">
          {!briefing.featured_image || imgError ? (
            <div className="w-full h-full bg-gradient-to-br from-slate-800 via-gray-900 to-black flex items-center justify-center">
              <span className="text-white text-9xl opacity-20">📋</span>
            </div>
          ) : (
            <img 
              src={briefing.featured_image}
              alt={`Briefing #${briefing.id}`}
              className="w-full h-full object-cover"
              onError={() => setImgError(true)}
            />
          )}
          
          {/* GRADIENTE OVERLAY */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
        </div>

        {/* Badge superior direito */}
        <div className="absolute top-6 right-6 z-10">
            {feedMeta && (
                <button
                    onClick={handleFeedClick}
                    className={`inline-block bg-white/90 backdrop-blur-md px-4 py-2 rounded-full text-sm font-semibold uppercase ${feedMeta.text_color} hover:bg-white transition-colors cursor-pointer`}
                >
                {feedMeta.display_name}
                </button>
            )}
        </div>

        {/* Conteúdo inferior */}
        <div className="absolute bottom-0 left-0 right-0 z-10 p-8">
          <div className="flex items-end justify-between">
            <h1 className="text-5xl font-bold text-white leading-tight">
              Briefing #{briefing.id}
            </h1>
            <span className="text-white/90 text-sm whitespace-nowrap ml-4">
              {formattedDate}
            </span>
          </div>
        </div>
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
                variant="grid"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BriefingPage;