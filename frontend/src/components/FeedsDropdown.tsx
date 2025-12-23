// src/components/FeedsDropdown.tsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Feed } from '../types/api';

function FeedsDropdown() {
  const [isOpen, setIsOpen] = useState(false); // Dropdown aberto ou fechado?
  const [feeds, setFeeds] = useState<Feed[]>([]); // Lista de feeds da API
  const [loading, setLoading] = useState(true); // Está carregando?
  const [error, setError] = useState<string | null>(null); // Algum erro?

  useEffect(() => {
    async function fetchFeeds() {
      try {
        setLoading(true);
        
        const response = await fetch('https://galdinho.news/api/feeds');
        
        if (!response.ok) {
          throw new Error('Erro ao carregar feeds');
        }
        
        const data = await response.json();
        
        setFeeds(data.feeds);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    }

    fetchFeeds();
  }, []);

  return (
    <div className="relative">
      {/* --- BOTÃO FEEDS --- */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="
          text-white font-medium
          hover:text-gray-200 
          transition-colors duration-200
          flex items-center gap-1
        "
      >
        FEEDS
        {/* Setinha (muda direção quando abre) */}
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* --- DROPDOWN MENU --- */}
      {isOpen && (
        <div className="
          absolute top-full mt-2 right-0
          bg-white rounded-lg shadow-lg
          min-w-[200px]
          py-2
        ">
          {/* Estado: Carregando */}
          {loading && (
            <div className="px-4 py-2 text-gray-500 text-sm">
              Carregando...
            </div>
          )}

          {/* Estado: Erro */}
          {error && (
            <div className="px-4 py-2 text-red-500 text-sm">
              {error}
            </div>
          )}

          {/* Estado: Sucesso - Lista de feeds */}
          {!loading && !error && feeds.map((feed) => (
            <Link
              key={feed.name}
              to={`/feeds/${feed.name}`}
              className="
                block px-4 py-2
                text-gray-700 hover:bg-blue-50 hover:text-blue-600
                transition-colors duration-150
              "
            >
              {feed.display_name}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default FeedsDropdown;