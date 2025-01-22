"use client"

import { useLocation } from "react-router-dom"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"


  
  // Then in formatBreadcrumb:
  function formatBreadcrumb(str: string, breadcrumbData: Record<string, string>): string {
    return breadcrumbData[str] ?? str
      .split("-")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

export function DynamicBreadcrumb({ breadcrumbData }: { breadcrumbData: Record<string, string> }) {
  const location = useLocation()
  const paths = location.pathname.split("/").filter(Boolean)

  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem className="hidden md:block">
          <BreadcrumbLink href="/">CredGem</BreadcrumbLink>
        </BreadcrumbItem>
        {paths.length > 0 && <BreadcrumbSeparator className="hidden md:block" />}
        {paths.map((path, index) => {
          const href = `/${paths.slice(0, index + 1).join("/")}`
          const isLast = index === paths.length - 1
          
          return (
            <BreadcrumbItem key={path}>
              {!isLast ? (
                <>
                  <BreadcrumbLink href={href}>
                    {formatBreadcrumb(path, breadcrumbData)}
                  </BreadcrumbLink>
                  <BreadcrumbSeparator />
                </>
              ) : (
                <BreadcrumbPage>{formatBreadcrumb(path, breadcrumbData)}</BreadcrumbPage>
              )}
            </BreadcrumbItem>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}

