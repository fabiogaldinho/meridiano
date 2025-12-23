// src/components/SkeletonArticleCard.tsx

function SkeletonArticleCard() {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse min-w-[280px] max-w-[340px]">
      
      {/* Imagem skeleton */}
      <div className="h-40 bg-gradient-to-br from-gray-300 to-gray-200" />

      {/* Conteúdo */}
      <div className="p-6">
        {/* Badges skeleton (dois badges lado a lado) */}
        <div className="flex items-center justify-between mb-3">
          <div className="h-6 w-16 bg-gray-200 rounded-full" />
          <div className="h-6 w-12 bg-gray-200 rounded-full" />
        </div>

        {/* Título skeleton */}
        <div className="space-y-2 mb-3">
          <div className="h-5 bg-gray-200 rounded w-full" />
          <div className="h-5 bg-gray-200 rounded w-4/5" />
        </div>

        {/* Data skeleton */}
        <div className="h-4 bg-gray-200 rounded w-32 mb-3" />

        {/* Preview skeleton */}
        <div className="space-y-2 mb-3">
          <div className="h-3 bg-gray-200 rounded w-full" />
          <div className="h-3 bg-gray-200 rounded w-full" />
          <div className="h-3 bg-gray-200 rounded w-3/4" />
        </div>

        {/* Link skeleton */}
        <div className="h-4 w-20 bg-gray-200 rounded" />
      </div>
    </div>
  );
}

export default SkeletonArticleCard;