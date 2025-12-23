// src/pages/ArticlePage.tsx
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import type { Article, Feed } from '../types';
import { getArticle, getFeeds } from '../services/api';
import SkeletonArticlePage from '../components/SkeletonArticlePage';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';

function ArticlePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [article, setArticle] = useState<Article | null>(null);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    async function fetchData() {
      if (!id) return;

      try {
        setLoading(true);

        const [articleData, feedsData] = await Promise.all([
          getArticle(parseInt(id)),
          getFeeds()
        ]);

        setArticle(articleData);
        setFeeds(feedsData);

      } catch (err) {
        console.error('Erro ao carregar artigo:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  if (loading) {
    return <SkeletonArticlePage />;
  }

  if (!article) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">❌</div>
          <p className="text-gray-600 mb-4">Artigo não encontrado</p>
          <Link to="/" className="text-blue-600 hover:underline">
            Voltar para Home
          </Link>
        </div>
      </div>
    );
  }

  const feedsByName = Object.fromEntries(feeds.map(f => [f.name, f]));
  const feedMeta = feedsByName[article.feed_profile];
  
  const formattedDate = new Date(article.published_date).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  // Handler para clicar no badge do feed
  const handleFeedClick = () => {
    navigate(`/feeds/${article.feed_profile}`);
  };

  return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Breadcrumb */}
            <nav className="text-sm text-gray-600 mb-6">
                <Link to="/" className="hover:text-blue-600">Home</Link>
                <span className="mx-2">/</span>
                <Link to={`/feeds/${article.feed_profile}`} className="hover:text-blue-600">
                    {feedMeta?.display_name || article.feed_profile}
                </Link>
                <span className="mx-2">/</span>
                <span className="text-gray-800">{article.title}</span>
            </nav>

            {/* Hero Image */}
            <div className="relative rounded-2xl overflow-hidden shadow-2xl mb-8 h-[400px]">
                <div className="absolute inset-0 z-0">
                    {!article.image_url || imgError ? (
                        <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <span className="text-white text-9xl opacity-20">📰</span>
                        </div>
                    ) : (
                        <img 
                            src={article.image_url}
                            alt={article.title}
                            className="w-full h-full object-cover"
                            onError={() => setImgError(true)}
                        />
                    )}
                
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                </div>

                {/* Badge de impact score */}
                {article.impact_score !== null && article.impact_score !== undefined && (
                    <div className="absolute top-6 left-6 z-10">
                        <span 
                            className={`
                                inline-block px-4 py-2 rounded-full text-base font-bold text-white
                                ${article.impact_score >= 9 ? 'bg-red-500' : 
                                article.impact_score >= 7 ? 'bg-orange-500' : 
                                article.impact_score >= 5 ? 'bg-yellow-500' : 'bg-gray-400'}
                            `}>
                            🔥 {article.impact_score}
                        </span>
                    </div>
                )}

                {/* Badge do feed */}
                {feedMeta && (
                    <div className="absolute top-6 right-6 z-10">
                        <button
                            onClick={handleFeedClick}
                            className={`inline-block bg-white/90 backdrop-blur-md px-4 py-2 rounded-full text-sm font-semibold uppercase ${feedMeta.text_color} hover:bg-white transition-colors cursor-pointer`}>
                            {feedMeta.display_name}
                        </button>
                    </div>
                )}

                {/* Conteúdo inferior */}
                <div className="absolute bottom-0 left-0 right-0 z-10 p-8">
                    <h1 className="text-4xl font-bold text-white leading-tight mb-2">
                        {article.title}
                    </h1>
                    <p className="text-white/90 text-sm">
                        {article.feed_source} • {formattedDate}
                    </p>
                </div>
            </div>

            {/* Summary */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-4"><b>RESUMO</b></h2>
            
                {article.processed_content && (
                    <div 
                        className="prose prose-lg max-w-none prose-p:text-gray-700"
                        dangerouslySetInnerHTML={{ __html: article.processed_content }}
                    />
                )}
            </div>

            {/* Raw Content */}
            {(article.formatted_content || article.raw_content) && (
                <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">ARTIGO COMPLETO</h2>
                    
                    <div className="prose prose-lg max-w-none prose-p:text-gray-700 prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw]}
                        components={{
                        a: ({ node, ...props }) => (
                            <a {...props} target="_blank" rel="noopener noreferrer" />
                        ),
                        p: ({ node, ...props }) => (
                            <p {...props} className="mb-4 leading-relaxed" />
                        ),
                        }}
                    >
                        {article.formatted_content || article.raw_content}
                    </ReactMarkdown>
                    </div>
                </div>
            )}

            {/* Links Section */}
            <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">LINKS</h2>
                
                <div className="space-y-4">
                    {/* Link Original */}
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                        </div>
                        <div className="flex-grow">
                            <p className="text-sm font-semibold text-gray-800 mb-1">Link Original</p>
                            <a 
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline text-sm break-all"
                            >
                                {article.url}
                            </a>
                        </div>
                    </div>

                    {/* Link Marreta */}
                    {article.marreta && article.url_encoding && (
                        <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="flex-grow">
                                <p className="text-sm font-semibold text-gray-800 mb-1">
                                Link via Marreta 
                                    <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-normal">
                                        Sem paywall
                                    </span>
                                </p>
                                <a 
                                    href={article.url_encoding}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-green-600 hover:underline text-sm break-all">
                                    {article.url_encoding}
                                </a>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ArticlePage;