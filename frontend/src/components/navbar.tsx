"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ModeToggle } from "@/components/mode-toggle"
import { useAuth } from "@/lib/auth"
import { Button } from "@/components/ui/button"

export function Navbar() {
  const pathname = usePathname()
  const { isAuthenticated, user, logout } = useAuth()

  const navItems = [
    {
      name: "Home",
      href: "/",
    },
    {
      name: "Scraper",
      href: "/scraper",
    },
    {
      name: "Jobs",
      href: "/jobs",
    },
    {
      name: "Scratchpad",
      href: "/scratchpad",
    },
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <span className="hidden font-bold sm:inline-block">
              Universal Agentic Web Scraper
            </span>
          </Link>
        </div>
        <nav className="flex items-center space-x-6 text-sm font-medium">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`transition-colors hover:text-foreground/80 ${
                pathname === item.href ? "text-foreground" : "text-foreground/60"
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center space-x-4">
          {isAuthenticated ? (
            <>
              <div className="text-sm text-foreground/60">
                <span className="hidden md:inline-block mr-2">
                  {user?.username}
                </span>
                <Link 
                  href="/profile" 
                  className={`transition-colors hover:text-foreground/80 ${
                    pathname === "/profile" ? "text-foreground" : "text-foreground/60"
                  }`}
                >
                  Profile
                </Link>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={logout}
                className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
              >
                Logout
              </Button>
            </>
          ) : (
            <Link href="/auth">
              <Button size="sm">Login / Register</Button>
            </Link>
          )}
          <ModeToggle />
        </div>
      </div>
    </header>
  )
} 