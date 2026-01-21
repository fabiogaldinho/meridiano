// src/components/HomeNewsletterGrid.tsx
import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Newsletter, Feed } from '../types';
import { getNewsletters, getFeeds } from '../services/api';

function HomeNewsletterGrid() {
  const [newsletters, setNewsletters] = useState<Newsletter[]>([]);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [newslettersData, feedsData] = await Promise.all([
          getNewsletters(),
          getFeeds()
        ]);
        
        // Pega apenas a última newsletter de cada feed
        const latestByFeed = feedsData.reduce((acc: Newsletter[], feed) => {
          const latest = newslettersData.find(n => n.feed_profile === feed.name);
          if (latest) acc.push(latest);
          return acc;
        }, []);

        // Ordena por generated_at DESC, depois feed_profile ASC
        latestByFeed.sort((a, b) => {
          const dateA = new Date(a.generated_at).toISOString().split('T')[0];
          const dateB = new Date(b.generated_at).toISOString().split('T')[0];
          
          const dateCompare = dateB.localeCompare(dateA);
          if (dateCompare !== 0) return dateCompare;
          
          return a.feed_profile.localeCompare(b.feed_profile);
        });
        
        setNewsletters(latestByFeed);
        setFeeds(feedsData);
      } catch (err) {
        console.error('Erro ao buscar newsletters:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const feedsByName = Object.fromEntries(
    feeds.map(feed => [feed.name, feed])
  );

  const checkScroll = () => {
    const container = scrollRef.current;
    if (!container) return;
    setCanScrollLeft(container.scrollLeft > 0);
    setCanScrollRight(container.scrollLeft < container.scrollWidth - container.clientWidth - 5);
  };

  useEffect(() => {
    if (newsletters.length > 0) {
      setTimeout(checkScroll, 100);
    }
  }, [newsletters]);

  const scroll = (direction: 'left' | 'right') => {
    const container = scrollRef.current;
    if (!container) return;
    const scrollAmount = container.clientWidth;
    container.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    });
  };

  if (loading) {
    return (
      <div className="my-8 -mx-6 md:-mx-12 lg:-mx-16">
        <div className="grid grid-cols-4 gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-[130px] rounded-xl bg-gray-200 dark:bg-slate-700 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (newsletters.length === 0) return null;

  return (
    <div className="mb-8 -mx-6 md:-mx-12 lg:-mx-16 relative group dark:shadow-[0_0_15px_rgba(59,130,246,0.3)] rounded-2xl">
      <div 
        ref={scrollRef}
        onScroll={checkScroll}
        className="flex overflow-x-auto scrollbar-hide scroll-smooth"
      >
        <div className="flex min-w-full">
          {newsletters.map((newsletter, index) => {
            const feedMeta = feedsByName[newsletter.feed_profile];
            const formattedDate = new Date(newsletter.generated_at).toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: 'short'
            });

            return (
              <div
                key={newsletter.id}
                onClick={() => navigate(`/newsletters/${newsletter.id}`)}
                className={`
                  relative h-[130px] cursor-pointer overflow-hidden
                  flex-1 min-w-[25%]
                  group/card
                  ${index === 0 ? 'rounded-l-2xl' : ''}
                  ${index === newsletters.length - 1 || index === 3 ? 'rounded-r-2xl' : ''}
                `}
              >
                {/* Background */}
                {newsletter.featured_image ? (
                  <img 
                    src={newsletter.featured_image}
                    alt="Newsletter"
                    className="w-full h-full object-cover group-hover/card:scale-105 group-hover/card:brightness-110 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-emerald-800 via-teal-900 to-cyan-950" />
                )}

                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent group-hover/card:from-black/50 group-hover/card:via-black/10 transition-all duration-500" />

                {/* Badge do feed */}
                {feedMeta && (
                  <span className={`
                    absolute top-3 left-3
                    bg-white/90 backdrop-blur-sm 
                    px-2 py-1 rounded-md 
                    text-xs font-semibold uppercase 
                    ${feedMeta.text_color}
                  `}>
                    {feedMeta.display_name}
                  </span>
                )}

                {/* Data */}
                <span className="absolute bottom-3 left-3 text-white text-sm font-medium group-hover/card:font-bold">
                  Newsletter {formattedDate}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Seta Esquerda */}
      {canScrollLeft && (
        <button
          onClick={() => scroll('left')}
          className="
            absolute left-2 top-1/2 -translate-y-1/2
            bg-white/90 dark:bg-slate-800/90 hover:bg-white dark:hover:bg-slate-700
            text-gray-800 dark:text-gray-100 p-2 rounded-full shadow-lg
            opacity-0 group-hover:opacity-100 transition-all duration-300 z-10
          "
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}

      {/* Seta Direita */}
      {canScrollRight && (
        <button
          onClick={() => scroll('right')}
          className="
            absolute right-2 top-1/2 -translate-y-1/2
            bg-white/90 dark:bg-slate-800/90 hover:bg-white dark:hover:bg-slate-700
            text-gray-800 dark:text-gray-100 p-2 rounded-full shadow-lg
            opacity-0 group-hover:opacity-100 transition-all duration-300 z-10
          "
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      )}
    </div>
  );
}

export default HomeNewsletterGrid;