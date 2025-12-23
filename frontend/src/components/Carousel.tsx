// src/components/Carousel.tsx
import { useState } from 'react';
import type { Briefing } from '../types';
import { useNavigate } from 'react-router-dom';

interface CarouselProps {
  briefings: Briefing[];
}

function Carousel({ briefings }: CarouselProps) {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imgError, setImgError] = useState(false);

  if (briefings.length === 0) {
    return null;
  }

  const currentBriefing = briefings[currentIndex];

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === briefings.length - 1 ? 0 : prevIndex + 1
    );
    setImgError(false);
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? briefings.length - 1 : prevIndex - 1
    );
    setImgError(false);
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
    setImgError(false);
  };

  return (
    <div className="relative w-full mb-8">
      {/* Container do carrossel */}
      <div className="relative h-96 rounded-2xl overflow-hidden shadow-2xl">
        
        {/* Imagem de fundo */}
        {!currentBriefing.featured_image || imgError ? (
          <div className="w-full h-full bg-gradient-to-br from-purple-900 via-violet-900 to-indigo-950 flex items-center justify-center">
            <span className="text-white text-9xl opacity-20">📋</span>
          </div>
        ) : (
          // Imagem de fundo
          <>
            <img 
              src={currentBriefing.featured_image}
              alt={`Briefing #${currentBriefing.id}`}
              className="absolute inset-0 w-full h-full object-cover"
              onError={() => setImgError(true)}
            />
            {/* Overlay escuro para texto (só quando tem imagem) */}
            <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-transparent" />
          </>
        )}

        {/* Conteúdo do slide atual */}
        <div className="absolute inset-0 flex items-center pl-24 pr-12">
          <div className="max-w-2xl text-white">
            
            {/* Badge do feed */}
            <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-bold uppercase mb-4">
              {currentBriefing.feed_profile}
            </span>

            {/* Título */}
            <h2 className="text-4xl font-bold mb-4">
              Briefing #{currentBriefing.id}
            </h2>

            {/* Preview do conteúdo */}
            <p className="text-lg mb-6 text-white/95">
              {currentBriefing.preview}
            </p>

            {/* Botão "Ler mais" */}
            <button 
              onClick={() => navigate(`/briefings/${currentBriefing.id}`)}
              className="inline-flex items-center gap-2 bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors w-fit"
            >
              Ler Briefing Completo
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Setas de navegação - Esquerda */}
        <button
          onClick={prevSlide}
          className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white p-3 rounded-full transition"
          aria-label="Anterior"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        {/* Setas de navegação - Direita */}
        <button
          onClick={nextSlide}
          className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white p-3 rounded-full transition"
          aria-label="Próximo"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Dots de navegação */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
          {briefings.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`
                w-3 h-3 rounded-full transition-all
                ${index === currentIndex 
                  ? 'bg-white w-8' 
                  : 'bg-white/50 hover:bg-white/75'}
              `}
              aria-label={`Ir para slide ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default Carousel;