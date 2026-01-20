// src/components/NewsletterCard.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Newsletter, Feed } from '../types';

interface NewsletterCardProps {
  newsletter: Newsletter;
  feedMeta?: Feed;
}

function NewsletterCard({ newsletter, feedMeta }: NewsletterCardProps) {
  const [imgError, setImgError] = useState(false);
  const navigate = useNavigate();

  const formattedDate = new Date(newsletter.generated_at).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short'
  });

  const handleClick = () => navigate(`/newsletters/${newsletter.id}`);

  const handleFeedClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/feeds/${newsletter.feed_profile}`);
  };

  return (
    <div 
      onClick={handleClick}
      className="
        flex-shrink-0 w-40 h-40 
        rounded-xl overflow-hidden 
        cursor-pointer relative
        shadow-md hover:shadow-xl 
        transition-all duration-300 
        hover:-translate-y-1
      "
    >
      {/* Background Image */}
      {!newsletter.featured_image || imgError ? (
        <div className="w-full h-full bg-gradient-to-br from-emerald-800 via-teal-900 to-cyan-950" />
      ) : (
        <img 
          src={newsletter.featured_image}
          alt="Newsletter"
          className="w-full h-full object-cover"
          onError={() => setImgError(true)}
        />
      )}

      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

      {/* Badge do feed */}
      {feedMeta && (
        <button
          onClick={handleFeedClick}
          className={`
            absolute top-2 left-2
            bg-white/90 backdrop-blur-sm 
            px-1.5 py-0.5 rounded-md 
            text-[10px] font-semibold uppercase 
            ${feedMeta.text_color} 
            hover:bg-white transition-colors
          `}
        >
          {feedMeta.display_name}
        </button>
      )}

      {/* Data */}
      <span className="absolute bottom-2 left-2 text-white text-xs font-medium">
        {formattedDate}
      </span>
    </div>
  );
}

export default NewsletterCard;