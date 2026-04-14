// src/components/FeedSection.tsx
import { useEffect, useState } from 'react';
import type { Briefing, Newsletter} from '../types';
import Carousel from './Carousel';
import TrendingSection from './TrendingSection';
import PaginatedArticles from './PaginatedArticles';
import SkeletonCarousel from './SkeletonCarousel';
import RecentNewsletters from './RecentNewsletters';

interface FeedSectionProps {
  feedProfile: string;
  title: string;
}

function FeedSection({ feedProfile, title }: FeedSectionProps) {
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [loadingBriefings, setLoadingBriefings] = useState(true);
  const [newsletter, setNewsletter] = useState<Newsletter | null>(null);

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

    async function fetchNewsletter() {
      try {
        const response = await fetch(`/api/newsletters?feed_profile=${feedProfile}&limit=1`);
        const data = await response.json();
        if (data.newsletters && data.newsletters.length > 0) {
          setNewsletter(data.newsletters[0]);
        }
      } catch (err) {
        console.error(`Erro ao buscar newsletter de ${feedProfile}:`, err);
      }
    }

    fetchBriefings();
    fetchNewsletter();
  }, [feedProfile]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header da página do feed */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100 flex items-center gap-3">
          <b>FEED {title.toUpperCase()}</b>
        </h1>
      </div>

      {/* Newsletter Banner */}
      {newsletter && (
        <a 
          href={`/newsletters/${newsletter.id}`}
          className="block mb-8 group -mx-3 md:-mx-12 lg:-mx-16 dark:shadow-[0_0_15px_rgba(59,130,246,0.3)] rounded-2xl"
        >
          <div className="relative rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300">
            {/* Background Image */}
            <div className="h-[130px]">
              {newsletter.featured_image ? (
                <img 
                  src={newsletter.featured_image}
                  alt="Newsletter"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-emerald-800 via-teal-900 to-cyan-950" />
              )}
              
              {/* Overlay gradiente */}
              <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent" />
            </div>

            {/* Conteúdo */}
            <div className="absolute inset-0 flex items-center p-6 md:p-8">
              <div className="max-w-2xl">
                {/* Título */}
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-2 mt-2">
                  Newsletter {new Date(newsletter.generated_at).toLocaleDateString('pt-BR')}
                </h2>
                
                {/* Preview */}
                <p className="text-white/80 text-sm md:text-base line-clamp-2 mb-4">
                  {newsletter.preview?.replace(/\*\*/g, '')}
                </p>
              </div>
            </div>
          </div>
        </a>
      )}

      {/* 1. Carrossel de Briefings */}
      {loadingBriefings ? (
        <SkeletonCarousel />
      ) : briefings.length > 0 ? (
        <Carousel briefings={briefings} />
      ) : null}

      {/* 2. Newsletters Recentes */}
      <RecentNewsletters
        feedProfile={feedProfile}
        title="NEWSLETTERS"
      />

      {/* 3. Principais Notícias */}
      <TrendingSection 
        title="PRINCIPAIS NOTÍCIAS"
        feedProfile={feedProfile}
        limit={10}
      />

      {/* 4. Todos os Artigos */}
      <PaginatedArticles 
        feedProfile={feedProfile}
        title="TODOS OS ARTIGOS"
      />
    </div>
  );
}

export default FeedSection;