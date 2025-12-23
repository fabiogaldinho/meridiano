// src/components/BriefingCard.tsx
import { useState } from 'react';
import type { Briefing, Feed } from '../types';

interface BriefingCardProps {
  briefing: Briefing;
  feedMeta?: Feed
  onClick?: () => void;
}


function BriefingCard({ briefing, feedMeta, onClick }: BriefingCardProps) {
    const formattedDate = new Date(briefing.generated_at).toLocaleDateString(
        'pt-BR',
        {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }
    );

    const [imgError, setImgError] = useState(false);

  return (
    <div 
      onClick={onClick}
      className={`
        bg-white rounded-xl shadow-md p-6 
        transition-all duration-300
        ${onClick ? 'cursor-pointer hover:shadow-xl hover:-translate-y-1' : ''}
      `}
    >
      {/* Imagem do artigo principal */}
      <div className="relative h-48 w-full">
        {!briefing.featured_image || imgError ? (
          <div className="w-full h-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <span className="text-white text-6xl opacity-50">📰</span>
          </div>
        ) : (
          <img
            src={briefing.featured_image}
            alt={`Briefing #${briefing.id}`}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        )}

        {/* Badge do feed profile */}
        <div className="absolute top-3 right-3">
          <span className={`
            inline-block px-3 py-1 rounded-full text-xs font-semibold bg-gray-100
            ${feedMeta?.text_color || 'text-gray-800'}
          `}>
            {feedMeta?.display_name || briefing.feed_profile.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Título do briefing */}
      <h3 className="text-xl font-bold text-gray-800 mb-2 mt-2">
        Briefing #{briefing.id}
      </h3>

      {/* Data */}
      <p className="text-gray-600 text-sm">
        {formattedDate}
      </p>

      {/* Preview do conteúdo (primeiras 150 caracteres) */}
      <p className="text-gray-700 mt-3 line-clamp-3">
        {briefing.preview}
      </p>

      {/* Link "Ler mais" se onClick foi passado */}
      {onClick && (
        <p className="text-blue-600 font-semibold mt-4 text-sm">
          Ler briefing completo →
        </p>
      )}
    </div>
  );
}

export default BriefingCard;