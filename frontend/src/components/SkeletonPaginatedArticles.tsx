// src/components/SkeletonPaginatedArticles.tsx
import SkeletonArticleCard from './SkeletonArticleCard';

function SkeletonPaginatedArticles() {
  return (
    <div className="my-12">
      {/* Título skeleton */}
      <div className="h-9 bg-gray-200 rounded w-72 mb-6 animate-pulse" />

      {/* Grid de skeletons */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <SkeletonArticleCard key={i} />
        ))}
      </div>
    </div>
  );
}

export default SkeletonPaginatedArticles;