import { ColumnDef } from "@tanstack/react-table";
import { Transaction } from "@/types/wallet";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { useWalletStore } from "@/store/useWalletStore";

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) => {
      const type = row.getValue("type") as string;
      return (
        <Badge variant={
          type === "deposit" ? "default" :
          type === "debit" ? "destructive" :
          type === "hold" ? "secondary" :
          type === "release" ? "outline" :
          "secondary"
        }>
          {type}
        </Badge>
      );
    },
  },
  {
    accessorKey: "credit_type_id",
    header: "Credit Type",
    cell: ({ row }) => {
      const { creditTypes } = useWalletStore();
      const creditTypeId = row.getValue("credit_type_id") as string;
      const creditType = creditTypes.find(ct => ct.id === creditTypeId);
      return creditType?.name || creditTypeId;
    },
  },
  {
    accessorKey: "amount",
    header: "Amount",
    cell: ({ row }) => {
      const amount = row.getValue("amount") as number;
      const type = row.getValue("type") as string;
      const prefix = type === "debit" ? "-" : "+";
      return <span className={type === "debit" ? "text-destructive" : "text-green-600"}>
        {prefix}{amount}
      </span>;
    },
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "issuer",
    header: "Issuer",
  },
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => {
      return formatDate(row.getValue("created_at"));
    },
  },
]; 