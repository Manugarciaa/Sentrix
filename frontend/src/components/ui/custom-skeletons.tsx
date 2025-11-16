import React from 'react'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/utils'

export const SkeletonDashboard: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-6 pb-16', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-4 w-72" />
        </div>
        <Skeleton className="h-9 w-28 rounded-lg" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-8 w-16" />
              </div>
              <Skeleton className="h-14 w-14 rounded-lg" />
            </div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Map and Trend */}
        <div className="lg:col-span-2 space-y-6">
          {/* Map */}
          <div className="bg-card rounded-2xl p-6 border border-border shadow-sm">
            <Skeleton className="h-96 md:h-[500px] rounded-xl" />
          </div>

          {/* Trend Chart */}
          <div className="bg-card border border-border rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-40" />
            </div>
            <Skeleton className="h-[250px] rounded-lg" />
          </div>
        </div>

        {/* Right Column - Stats */}
        <div className="space-y-6">
          {/* Risk Distribution */}
          <div className="bg-card border border-border rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-48" />
            </div>
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-3 w-3 rounded-full" />
                      <Skeleton className="h-4 w-16" />
                    </div>
                    <Skeleton className="h-4 w-8" />
                  </div>
                  <Skeleton className="h-2.5 w-full rounded-full" />
                </div>
              ))}
            </div>
          </div>

          {/* Detection Types */}
          <div className="bg-card border border-border rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-44" />
            </div>
            <Skeleton className="h-[200px] rounded-lg mb-4" />
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center gap-2 p-2 rounded-lg">
                  <Skeleton className="h-3 w-3 rounded-full" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-8" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export const SkeletonAnalysisList: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-2">
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-5 w-72" />
        </div>
        <Skeleton className="h-10 w-40 rounded-lg" />
      </div>

      {/* Filter Bar - Horizontal Row Layout */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        {/* Header */}
        <div className="px-4 py-3 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-4 rounded" />
              <Skeleton className="h-4 w-16" />
            </div>
            <Skeleton className="h-8 w-20 rounded-lg" />
          </div>
        </div>
        {/* Filters - Horizontal grid */}
        <div className="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="space-y-1.5">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="h-9 rounded-lg" />
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Cards Grid - Compact Horizontal Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-card border border-border rounded-lg overflow-hidden shadow-sm">
            <div className="flex gap-3 p-3">
              {/* Image Thumbnail Skeleton */}
              <Skeleton className="w-24 h-24 rounded-md flex-shrink-0" />

              {/* Content Skeleton */}
              <div className="flex-1 min-w-0 flex flex-col justify-between">
                {/* Header */}
                <div>
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </div>

                  {/* Metadata compacta */}
                  <div className="flex items-center gap-3 mb-1">
                    <Skeleton className="h-3 w-20" />
                    <Skeleton className="h-3 w-8" />
                  </div>

                  <Skeleton className="h-3 w-32" />
                </div>

                {/* Footer */}
                <Skeleton className="h-3 w-28" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export const SkeletonImagePreview: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('bg-card border border-border rounded-xl shadow-sm p-5 sm:p-7', className)}>
      <div className="flex justify-between items-start mb-5 sm:mb-6">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-1/3" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <Skeleton className="h-10 w-10 rounded-full" />
      </div>

      {/* Image placeholder */}
      <Skeleton className="w-full h-[400px] sm:h-[500px] mb-5 sm:mb-6 rounded-xl" />

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <Skeleton className="flex-1 h-11 rounded-lg" />
        <Skeleton className="sm:w-auto w-full h-11 rounded-lg" />
      </div>
    </div>
  )
}

export const SkeletonAnalysisDetail: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Skeleton className="h-9 w-24 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Skeleton className="h-9 w-20 rounded-lg" />
          <Skeleton className="h-9 w-20 rounded-lg" />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Skeleton className="h-9 w-9 rounded-lg" />
              <div className="space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-7 w-12" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="bg-card border border-border rounded-lg p-1">
        <div className="flex gap-2">
          <Skeleton className="h-9 w-24 rounded-lg" />
          <Skeleton className="h-9 w-24 rounded-lg" />
          <Skeleton className="h-9 w-24 rounded-lg" />
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Skeleton className="h-96 rounded-xl" />
        <div className="space-y-4">
          <Skeleton className="h-48 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
        </div>
      </div>
    </div>
  )
}

export const SkeletonAnalysisResults: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-4 sm:space-y-5', className)}>
      <div className="bg-card rounded-xl border border-border shadow-sm p-5 sm:p-7">
        <div className="flex justify-between items-start mb-6">
          <div className="space-y-2">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-10 w-10 rounded-full" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6">
          {/* Image skeleton */}
          <Skeleton className="w-full h-[400px] sm:h-[450px] lg:h-[500px] rounded-xl" />

          {/* Stats and info skeleton */}
          <div className="space-y-4">
            {/* Stats cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="p-4 sm:p-5 rounded-xl border-2 border-border bg-muted/20">
                  <Skeleton className="h-3 w-20 mb-2" />
                  <Skeleton className="h-8 w-16" />
                </div>
              ))}
            </div>

            {/* Details panel */}
            <div className="p-4 sm:p-5 rounded-xl bg-muted/20 border-2 border-border space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Skeleton className="h-4 w-4 rounded-full" />
                <Skeleton className="h-4 w-32" />
              </div>
              <div className="space-y-2.5">
                {Array.from({ length: 2 }).map((_, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-muted/40">
                    <Skeleton className="h-3 w-full" />
                  </div>
                ))}
              </div>
            </div>

            {/* CTA skeleton */}
            <div className="p-5 rounded-xl bg-muted/20 border-2 border-border space-y-3">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-10 w-full rounded-lg" />
            </div>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <Skeleton className="flex-1 h-11 rounded-lg" />
        <Skeleton className="flex-1 h-11 rounded-lg" />
      </div>
    </div>
  )
}
