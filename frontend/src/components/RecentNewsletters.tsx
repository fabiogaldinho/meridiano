// src/components/RecentNewsletters.tsx
import { useEffect, useState } from 'react';
import type { Newsletter, Feed } from '../types';
import { getNewsletters, getFeeds } from '../services/api';
import NewsletterCard from './NewsletterCard';

interface RecentNewslettersProps {
  feedProfile?: string;
  title?: string;
}

function RecentNewsletters({ feedProfile, title = "NEWSLETTERS" }: RecentNewslettersProps) {
  const [newsletters, setNewsletters] = useState<Newsletter[]>([]);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [newslettersData, feedsData] = await Promise.all([
          getNewsletters(feedProfile),
          getFeeds()
        ]);
        setNewsletters(newslettersData);
        setFeeds(feedsData);
      } catch (err) {
        console.error('Erro ao buscar newsletters:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [feedProfile]);

  const feedsByName = Object.fromEntries(
    feeds.map(feed => [feed.name, feed])
  );

  if (loading) {
    return (
      <div className="my-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6">
          <b>{title}</b>
        </h2>
        <div className="flex gap-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex-shrink-0 w-32 h-32 rounded-xl bg-gray-200 dark:bg-slate-700 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (newsletters.length === 0) {
    return null;
  }

  return (
    <div className="my-8">
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6">
        <b>{title}</b>
      </h2>
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
        {newsletters.map((newsletter) => (
          <NewsletterCard
            key={newsletter.id}
            newsletter={newsletter}
            feedMeta={feedsByName[newsletter.feed_profile]}
          />
        ))}
      </div>
    </div>
  );
}

export default RecentNewsletters;