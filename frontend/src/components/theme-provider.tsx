"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider, type ThemeProviderProps } from "next-themes"

export function ThemeProvider({ 
  children,
  ...props
}: {
  children: React.ReactNode;
} & ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
} 