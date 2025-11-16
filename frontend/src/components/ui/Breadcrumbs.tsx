import React from 'react'
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'

export interface BreadcrumbItemType {
  label: string
  href?: string
  current?: boolean
}

export interface BreadcrumbsProps {
  items: BreadcrumbItemType[]
  className?: string
  showHome?: boolean
  homeHref?: string
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  className,
  showHome = true,
  homeHref = '/app/dashboard',
}) => {
  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {showHome && (
          <>
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link to={homeHref} className="flex items-center">
                  <Home className="h-4 w-4" />
                  <span className="sr-only">Home</span>
                </Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
          </>
        )}

        {items.map((item, index) => {
          const isLast = index === items.length - 1
          const isCurrent = item.current || isLast

          return (
            <React.Fragment key={index}>
              <BreadcrumbItem>
                {item.href && !isCurrent ? (
                  <BreadcrumbLink asChild>
                    <Link to={item.href}>{item.label}</Link>
                  </BreadcrumbLink>
                ) : (
                  <BreadcrumbPage>{item.label}</BreadcrumbPage>
                )}
              </BreadcrumbItem>

              {!isLast && <BreadcrumbSeparator />}
            </React.Fragment>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}

export default Breadcrumbs
