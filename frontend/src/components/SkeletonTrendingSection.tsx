// src/components/SkeletonTrendingSection.tsx
import SkeletonArticleCard from './SkeletonArticleCard';

function SkeletonTrendingSection() {
  return (
    <div className="my-12">
      {/* Título skeleton */}
      <div className="h-9 bg-gray-200 rounded w-64 mb-6 animate-pulse" />

      {/* Grid de skeletons */}
      <div className="flex gap-4 overflow-hidden">
        {[1, 2, 3, 4].map((i) => (
          <SkeletonArticleCard key={i} />
        ))}
      </div>
    </div>
  );
}

export default SkeletonTrendingSection;