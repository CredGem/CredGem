import { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { Skeleton } from "@/components/ui/skeleton";
import { useTransactionStore } from "@/store/useTransactionStore";
import { Transaction, TransactionsQueryParams } from "@/types/wallet";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { toast } from "@/hooks/use-toast";
import { CreditType } from "@/types/creditType";





export default function Transactions() {
  const { 
    transactions, 
    isLoading, 
    error, 
    fetchTransactions,
    totalTransactions,
    currentPage,
    pageSize
  } = useTransactionStore();

  const { creditTypes, fetchCreditTypes, getCreditTypeName } = useWalletStore();
  const [selectedCreditType, setSelectedCreditType] = useState<string>("");
  const [selectedTimeRange, setSelectedTimeRange] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortDescriptor, setSortDescriptor] = useState<SortDescriptor>({
    column: "created_at",
    direction: "descending",
  });

  const [enrichedTransactions, setEnrichedTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    const _enrichedTransactions = transactions.map((transaction) => ({
      ...transaction,
      credit_type: creditTypes.find((type) => type.id === transaction.credit_type_id)?.name || "Unknown",
    }));
    setEnrichedTransactions(_enrichedTransactions);
  }, [transactions, creditTypes]);

    useEffect(() => {
    const loadCreditTypes = async () => {
      try {
        const types = await fetchCreditTypes();
        const creditTypesRes = {};
        types.forEach((type) => {
            creditTypesRes[type.id] = type;
        });
        setCreditTypes(creditTypesRes);
      } catch (error) {
        toast({
          title: "Error loading credit types",
          description: "Failed to load available credit types",
          variant: "destructive",
        });
      }
    };
    loadCreditTypes();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const params: TransactionsQueryParams = {
        page: currentPage.toString(),
        page_size: pageSize.toString()
      };

      if (selectedCreditType) {
        params.credit_type_id = selectedCreditType;
      }

      // Apply time range filter
      if (selectedTimeRange !== "all") {
        const now = new Date();
        const hours = {
          "24h": 24,
          "7d": 24 * 7,
          "30d": 24 * 30
        }[selectedTimeRange] || 0;

        if (hours) {
          const timeLimit = new Date(now.getTime() - hours * 60 * 60 * 1000);
          params.start_date = timeLimit.toISOString();
        }
      }

      await fetchTransactions(params);
    };

    fetchData();
  }, [fetchTransactions, selectedCreditType, selectedTimeRange, currentPage, pageSize]);

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Transactions</h1>
        <p className="text-sm text-muted-foreground">View all your transactions</p>
      </div>
      <div className="container mx-auto py-2">
        {isLoading ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading wallets: {error}</div>
        ) : (
          <DataTable 
            columns={columns} 
            data={enrichedTransactions} 
            creditTypes={creditTypes}
          />
        )}
      </div>
    </div>
  )
}
