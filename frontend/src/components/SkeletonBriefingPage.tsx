// src/components/SkeletonBriefingPage.tsx

function SkeletonBriefingPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb skeleton */}
      <div className="flex gap-2 mb-6">
        <div className="h-4 bg-gray-200 rounded w-16 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-1 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-20 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-1 animate-pulse" />
        <div className="h-4 bg-gray-200 rounded w-24 animate-pulse" />
      </div>

      {/* Featured image skeleton */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
        <div className="h-96 bg-gray-200 animate-pulse" />
      </div>

      {/* Content skeleton */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse" />
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse mt-8" />
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
        </div>
      </div>

      {/* Related articles skeleton */}
      <div className="mt-12">
        <div className="h-8 bg-gray-200 rounded w-64 mb-6 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-64 bg-gray-200 rounded-xl animate-pulse" />
          <div className="h-64 bg-gray-200 rounded-xl animate-pulse" />
        </div>
      </div>
    </div>
  );
}

export default SkeletonBriefingPage;