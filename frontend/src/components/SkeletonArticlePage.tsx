// src/components/SkeletonArticlePage.tsx

function SkeletonArticlePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb skeleton */}
      <div className="flex gap-2 mb-6">
        <div className="h-4 bg-gray-200 rounded w-16 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-1 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-20 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-1 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-32 animate-pulse" />
      </div>

      {/* Hero image skeleton */}
      <div className="relative rounded-2xl overflow-hidden shadow-2xl mb-8 h-[400px] bg-gray-200 animate-pulse" />

      {/* Summary section skeleton */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="h-6 bg-gray-200 rounded w-48 mb-4 animate-pulse" />
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse" />
        </div>
      </div>

      {/* Raw content skeleton */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="h-6 bg-gray-200 rounded w-64 mb-4 animate-pulse" />
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse" />
        </div>
      </div>
    </div>
  );
}

export default SkeletonArticlePage;