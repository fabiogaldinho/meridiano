// src/components/SkeletonFeedPage.tsx
import SkeletonCarousel from './SkeletonCarousel';
import SkeletonArticleCard from './SkeletonArticleCard';

function SkeletonFeedPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Título da página skeleton */}
      <div className="h-12 bg-gray-200 rounded w-64 mb-8 animate-pulse" />

      {/* Carousel skeleton */}
      <SkeletonCarousel />

      {/* Título "Principais Notícias" skeleton */}
      <div className="h-9 bg-gray-200 rounded w-72 mb-6 animate-pulse" />

      {/* Grid de artigos skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <SkeletonArticleCard key={i} />
        ))}
      </div>

      {/* Pagination skeleton */}
      <div className="flex justify-center items-center gap-2 mt-12">
        <div className="h-10 w-24 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-10 w-10 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-10 w-10 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-10 w-10 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-10 w-24 bg-gray-200 rounded animate-pulse"></div>
      </div>
    </div>
  );
}

export default SkeletonFeedPage;