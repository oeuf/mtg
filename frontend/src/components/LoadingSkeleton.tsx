interface TextSkeletonProps {
  width?: string;
}

export function CardSkeleton() {
  return (
    <div data-testid="card-skeleton" className="animate-pulse rounded-lg bg-gray-700 h-48" />
  );
}

export function TextSkeleton({ width = 'w-full' }: TextSkeletonProps) {
  return (
    <div className={`animate-pulse rounded bg-gray-700 h-4 ${width}`} />
  );
}

interface GridSkeletonProps {
  count?: number;
}

export function GridSkeleton({ count = 8 }: GridSkeletonProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }, (_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}
