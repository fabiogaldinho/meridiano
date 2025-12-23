// src/components/SkeletonCarousel.tsx

function SkeletonCarousel() {
  return (
    <div className="relative w-full mb-8">
      <div className="relative h-96 rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-gray-300 via-gray-200 to-gray-300 animate-pulse">
        
        {/* Área do conteúdo (lado esquerdo) */}
        <div className="absolute inset-0 flex items-center pl-24 pr-12">
          <div className="max-w-2xl space-y-4">
            
            {/* Badge skeleton */}
            <div className="h-8 w-24 bg-white/30 rounded-full" />

            {/* Título skeleton */}
            <div className="space-y-3">
              <div className="h-10 bg-white/40 rounded w-3/4" />
              <div className="h-10 bg-white/40 rounded w-1/2" />
            </div>

            {/* Preview skeleton */}
            <div className="space-y-2 mt-4">
              <div className="h-4 bg-white/30 rounded w-full" />
              <div className="h-4 bg-white/30 rounded w-5/6" />
            </div>

            {/* Botão skeleton */}
            <div className="h-12 w-56 bg-white/40 rounded-lg mt-6" />
          </div>
        </div>

        {/* Dots skeleton */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div 
              key={i} 
              className={`rounded-full bg-white/50 ${i === 1 ? 'w-8 h-3' : 'w-3 h-3'}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default SkeletonCarousel;