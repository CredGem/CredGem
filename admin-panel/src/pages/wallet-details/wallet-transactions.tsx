import { useEffect, useState } from "react";
import { useTransactionStore } from "@/store/useTransactionStore";
import { DataTable } from "@/components/ui/data-table";
import { columns } from "./columns";
import { Loader2 } from "lucide-react";

type WalletTransactionsProps = {
  walletId: string;
};

export function WalletTransactions({ walletId }: WalletTransactionsProps) {
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const {
    transactions,
    isLoading,
    error,
    fetchTransactions,
  } = useTransactionStore();

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        await fetchTransactions({
          wallet_id: walletId,
          page: 1,
          page_size: 10,
        });
      } finally {
        setIsFirstLoad(false);
      }
    };
    loadTransactions();
  }, [walletId, fetchTransactions]);

  if (error) {
    return <div className="text-red-500">Error loading transactions: {error}</div>;
  }

  return (
    <div className="space-y-4 ml-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Latest Transactions</h2>
      </div>
      <DataTable
        data={transactions}
        columns={columns}
        loadingSpinner={!isFirstLoad && isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      />
    </div>
  );
} 