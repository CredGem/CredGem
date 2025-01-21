import { AppSidebar } from "@/components/app-sidebar"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { ModeToggle } from "./mode-toggle"
import { RainbowButton } from "./ui/rainbow-button"
import { DynamicBreadcrumb } from "./breadcrums-dynamic"
import { GalleryVerticalEnd, AudioWaveform, Command, Gauge, Wallet, ArrowRightLeft, Coins, Terminal, Package } from "lucide-react"

export const navData = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  env: [
    {
      name: "Development",
      logo: GalleryVerticalEnd,
    },
    {
      name: "Staging",
      logo: AudioWaveform,
    },
    {
      name: "Production",
      logo: Command,
    },
  ],
  navMain: [
    {
      title: "Dashboard",
      url: "/",
      icon: Gauge,
      items: []
    },
    {
      title: "Wallets",
      url: "/wallets",
      icon: Wallet,
      items: []
    },
    {
      title: "Products",
      url: "/products",
      icon: Package,
      items: []
    },
    {
      title: "Transactions",
      url: "/transactions",
      icon: ArrowRightLeft,
      items: []
    },
    {
      title: "Credits",
      url: "/credits",
      icon: Coins,
      items: []
    },
    {
      title: "Playground",
      url: "/playground",
      icon: Terminal,
      items: []
    }
  ],
}       

const BREADCRUMB_MAPPING: Record<string, string> = {
  "": "Dashboard",
  "wallets": "Wallets Management",
  "wallet-details": "Wallet Details",
  "products": "Products Management",
  "transactions": "Transactions",
  "credits": "Credits",
  // Add more mappings as needed
}

export default function SidebarSc({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar navData={navData} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <DynamicBreadcrumb breadcrumbData={BREADCRUMB_MAPPING} />
          </div>
          <div className="ml-auto flex items-center gap-2 px-4">
            <RainbowButton className="h-8">Star On Github</RainbowButton>
            <ModeToggle />
          </div>
        </header>
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}
