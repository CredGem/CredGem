import { NextUIProvider } from '@nextui-org/react'
import { ReactNode } from 'react'

export function Providers({ children }: { children: ReactNode }) {
  return (
    <NextUIProvider>
      {children}
    </NextUIProvider>
  )
} 