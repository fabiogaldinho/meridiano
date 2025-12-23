// src/pages/Home.tsx
import { useEffect, useState } from 'react';
import type { Briefing } from '../types';
import Carousel from '../components/Carousel';
import TrendingSection from '../components/TrendingSection';
import PaginatedArticles from '../components/PaginatedArticles';
import SkeletonCarousel from '../components/SkeletonCarousel';

function Home() {
  // Estado para guardar a lista de briefings
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  
  // Estado para controlar se está carregando
  const [loading, setLoading] = useState(true);
  
  // Estado para guardar erros
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBriefings() {
      try {
        setLoading(true); // Marca como "carregando"

        const response = await fetch('/api/briefings?limit=6');
        const data = await response.json();
        setBriefings(data.briefings);
        setError(null); // Limpa qualquer erro anterior

      } catch (err) {
        setError('Erro ao carregar briefings. Tente novamente.');
        console.error('Erro:', err);
        
      } finally {
        setLoading(false); // Marca como fim do "carregamento"
      }
    }

    fetchBriefings();
  }, []);


  // Tratamento de erro
  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="text-4xl mb-4">❌</div>
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }


  // RETURN = MOSTRAR DADOS
  return (
      <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Carrossel */}
          {loading ? (
              <SkeletonCarousel />
            ) : briefings.length > 0 ? (
              <Carousel briefings={briefings} />
            ) : null
          }

          {/* Principais Notícias */}
          <TrendingSection 
            title="Principais Notícias"
            limit={10}
          />

          {/* Todos os Artigos */}
          <PaginatedArticles title="Todos os Artigos" />
      </div>
  );
}

export default Home;