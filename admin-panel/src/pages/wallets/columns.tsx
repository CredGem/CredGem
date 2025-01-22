import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useNavigate } from "react-router-dom"


export type Wallet = {
    id: string
    name: string
    status: "active" | "inactive"
    context: Record<string, string>
    lastActivity: string
}


export const columns: ColumnDef<Wallet>[] = [
    {
        accessorKey: "id",
        header: "ID",
        cell: ({ row }) => {
            return <div className="text-sm font-medium text-muted-foreground">{row.getValue("id")}</div>
        },
    },
    {
        accessorKey: "name",
        header: ({ column }) => {
            return (
              <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
              >
                Name
                <ArrowUpDown className="ml-2 h-4 w-4" />
              </Button>
            )
          },
    },
    {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => {
            const status = row.getValue("status") as string;
            return <Badge>{status}</Badge>
        },
    },
    {
        accessorKey: "context",
        header: "Context",
        cell: ({ row }) => {
            const context = row.getValue("context") as Record<string, string>;
            return Object.entries(context).map(([key, value]) => {
                return <Badge variant="outline">{key}: {value}</Badge>
            })
        },
    },
    {
        accessorKey: "updated_at",
        header: ({ column }) => {
            return (
              <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
              >
                Last Activity
                <ArrowUpDown className="ml-2 h-4 w-4" />
              </Button>
            )
          },
    },
    {
        accessorKey: "actions",
        header: "Actions",
    },
    {
        id: "actions",
        cell: ({ row }) => {
          const wallet = row.original
          const navigate = useNavigate()
     
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuItem
                  onClick={() => navigator.clipboard.writeText(wallet.id)}
                >
                  Copy wallet ID
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => navigate(`/wallets/${wallet.id}`)}
                >
                  View wallet details
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
]
