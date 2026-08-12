import { PhotoGridSkeleton, CardSkeleton } from '@/components/ui/Loading';

export default function Loading() {
  return (
    <div className="min-h-dvh flex flex-col bg-basalt">
      <div className="h-14 bg-basalt border-b border-surface-border" />
      <div className="flex-1 w-full max-w-7xl mx-auto px-8 py-12 flex flex-col gap-10">
        <div className="h-12 skeleton w-64 rounded-md" />
        <div className="grid grid-cols-3 gap-4">
          {[0, 1, 2].map(i => <CardSkeleton key={i} />)}
        </div>
        <PhotoGridSkeleton count={10} />
      </div>
    </div>
  );
}
