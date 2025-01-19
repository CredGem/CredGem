import * as React from "react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
import { EnvironmentSwitcher } from "./env-switcher"


export function AppSidebar({ navData, ...props }: React.ComponentProps<typeof Sidebar> & { navData: any }) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <EnvironmentSwitcher envs={navData.env} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navData.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={navData.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
