// src/components/FeedSection.tsx
import { useEffect, useState } from 'react';
import type { Briefing } from '../types';
import Carousel from './Carousel';
import TrendingSection from './TrendingSection';
import PaginatedArticles from './PaginatedArticles';
import SkeletonCarousel from './SkeletonCarousel';

interface FeedSectionProps {
  feedProfile: string;
  title: string;
}

function FeedSection({ feedProfile, title }: FeedSectionProps) {
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [loadingBriefings, setLoadingBriefings] = useState(true);

  useEffect(() => {
    async function fetchBriefings() {
      try {
        setLoadingBriefings(true);
        const response = await fetch(`/api/briefings?feed_profile=${feedProfile}&limit=5`);
        const data = await response.json();
        setBriefings(data.briefings);
      } catch (err) {
        console.error(`Erro ao buscar briefings de ${feedProfile}:`, err);
      } finally {
        setLoadingBriefings(false);
      }
    }

    fetchBriefings();
  }, [feedProfile]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header da página do feed */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
          <b>FEED {title.toUpperCase()}</b>
        </h1>
      </div>

      {/* 1. Carrossel de Briefings */}
      {loadingBriefings ? (
        <SkeletonCarousel />
      ) : briefings.length > 0 ? (
        <Carousel briefings={briefings} />
      ) : null}

      {/* 2. Principais Notícias */}
      <TrendingSection 
        title="Principais Notícias"
        feedProfile={feedProfile}
        limit={10}
      />

      {/* 3. Todos os Artigos */}
      <PaginatedArticles 
        feedProfile={feedProfile}
        title="Todos os Artigos"
      />
    </div>
  );
}

export default FeedSection;