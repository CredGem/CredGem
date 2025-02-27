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
import { TransactionType } from "@/types/wallet"






export type Transaction = {
    id: string
    type: TransactionType
    credit_type_id: string
    external_id: string | null
    hold_status: string | null
    status: "active" | "inactive"
    context: Record<string, string>
    payload: {
        type: string
        amount: number
    }
    description: string
    created_at: string
    updated_at: string
}



export const columns: ColumnDef<Transaction>[] = [
    {
        accessorKey: "id",
        header: "ID",
        cell: ({ row }) => (
            <div className="text-sm font-medium text-muted-foreground">{row.getValue("id")}</div>
        ),
    },
    {
        accessorKey: "type",
        header: ({ column }) => (
            <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
                Type
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
        cell: ({ row }) => (
            <Badge variant={row.getValue("type")}>{row.getValue("type")}</Badge>
        ),
    },
    {
        accessorKey: "credit_type",
        header: "Credit Type",
        cell: ({ row }) => (
           <div className="text-sm font-medium text-muted-foreground">{row.getValue("credit_type")}</div>
        ),
        meta: {
          filterVariant: 'select',
        }
    },
    {
        accessorKey: "external_id",
        header: "External ID",
        cell: ({ row }) => {
            const externalId = row.getValue("external_id") as string | null
            return <div>{externalId || "-"}</div>
        },
    },
    {
        accessorKey: "hold_status",
        header: "Hold Status",
        cell: ({ row }) => {
            const holdStatus = row.getValue("hold_status") as string | null
            return <Badge variant="outline">{holdStatus || "No Hold"}</Badge>
        },
    },
    {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => {
            const status = row.getValue("status") as "active" | "inactive"
            return <Badge variant={status === "active" ? "default" : "secondary"}>{status}</Badge>
        },
    },
    {
        accessorKey: "payload",
        header: "Amount",
        cell: ({ row }) => {
            const payload = row.getValue("payload") as Transaction["payload"]
            return <div>{payload.amount}</div>
        },
    },
    {
        accessorKey: "description",
        header: "Description",
    },
    {
        accessorKey: "context",
        header: "Context",
        cell: ({ row }) => {
            const context = row.getValue("context") as Record<string, string>
            return (
                <div className="flex gap-1 flex-wrap">
                    {Object.entries(context).map(([key, value], index) => (
                        <Badge key={index} variant="outline">
                            {key}: {value}
                        </Badge>
                    ))}
                </div>
            )
        },
    },
    {
        accessorKey: "created_at",
        header: ({ column }) => (
            <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
                Created At
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
    },
    {
        accessorKey: "updated_at",
        header: ({ column }) => (
            <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
                Updated At
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const transaction = row.original
     
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
                            onClick={() => navigator.clipboard.writeText(transaction.id)}
                        >
                            Copy transaction ID
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            onClick={() => navigate(`/transactions/${transaction.id}`)}
                        >
                            View transaction details
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
