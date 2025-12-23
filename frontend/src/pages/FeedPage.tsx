// src/pages/FeedPage.tsx
import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { Feed } from '../types/api';
import FeedSection from '../components/FeedSection';

function FeedPage() {
  const { feedName } = useParams<{ feedName: string }>();
  
  const [feedInfo, setFeedInfo] = useState<Feed | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchFeedInfo() {
      try {
        setLoading(true);
        const response = await fetch('/api/feeds');
        const data = await response.json();
        
        // Encontra o feed específico
        const feed = data.feeds.find((f: Feed) => f.name === feedName);
        setFeedInfo(feed || null);
      } catch (err) {
        console.error('Erro ao buscar info do feed:', err);
      } finally {
        setLoading(false);
      }
    }

    if (feedName) {
      fetchFeedInfo();
    }
  }, [feedName]);

  if (!feedName || (!loading && !feedInfo)) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Feed não encontrado</h1>
        <a href="/" className="text-blue-600 hover:underline">
          Voltar para a home
        </a>
      </div>
    );
  }

  return (
    <FeedSection
      feedProfile={feedName}
      title={feedInfo!.display_name}
    />
  );
}

export default FeedPage;