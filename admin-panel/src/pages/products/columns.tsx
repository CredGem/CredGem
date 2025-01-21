import { ColumnDef } from "@tanstack/react-table"
import { Product } from "@/types/product"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/lib/utils"

export const columns: ColumnDef<Product>[] = [
  {
    accessorKey: "id",
    header: "ID",
  },
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      return (
        <Badge variant={status === "ACTIVE" ? "default" : "secondary"}>
          {status.toLowerCase()}
        </Badge>
      )
    },
  },
  {
    accessorKey: "created_at",
    header: "Created At",
    cell: ({ row }) => {
      return formatDate(row.getValue("created_at"))
    },
  },
  {
    accessorKey: "settings",
    header: "Credit Types",
    cell: ({ row }) => {
      const settings = row.getValue("settings") as Product["settings"]
      return settings.length
    },
  },
] 