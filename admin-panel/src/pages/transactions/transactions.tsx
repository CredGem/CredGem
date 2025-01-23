import { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { Skeleton } from "@/components/ui/skeleton";
import { useTransactionStore } from "@/store/useTransactionStore";
import { Transaction, TransactionsQueryParams } from "@/types/wallet";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { toast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";
import { useDebounce } from "@/lib/utils";

export default function Transactions() {
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const { 
    transactions, 
    isLoading, 
    error, 
    fetchTransactions,
    totalTransactions,
    currentPage,
    pageSize,
    setPage
  } = useTransactionStore();

  const { creditTypes, fetchCreditTypes } = useWalletStore();
  const [selectedCreditType, setSelectedCreditType] = useState<string | undefined>(undefined);
  const [selectedTimeRange, setSelectedTimeRange] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500); // 500ms delay

  const [enrichedTransactions, setEnrichedTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    const _enrichedTransactions = transactions.map((transaction) => ({
      ...transaction,
      credit_type: creditTypes.find((type) => type.id === transaction.credit_type_id)?.name || "Unknown",
      external_transaction_id: null,
      hold_status: null,
      status: "active" as const,
    }));
    setEnrichedTransactions(_enrichedTransactions);
  }, [transactions, creditTypes]);

  useEffect(() => {
    const loadCreditTypes = async () => {
      try {
        await fetchCreditTypes();
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

      if (debouncedSearchQuery) {
        params.search = debouncedSearchQuery;
      }

      // Apply time range filter
      if (selectedTimeRange !== "all") {
        const now = new Date();
        const endDate = new Date(now);
        endDate.setHours(23, 59, 59, 999); // Set to end of day

        const hours = {
          "24h": 24,
          "7d": 24 * 7,
          "30d": 24 * 30
        }[selectedTimeRange] || 0;

        if (hours) {
          const startDate = new Date(now);
          startDate.setHours(startDate.getHours() - hours);
          startDate.setHours(0, 0, 0, 0); // Set to start of day
          
          params.start_date = startDate.toISOString();
          params.end_date = endDate.toISOString();
        }
      }

      await fetchTransactions(params);
      if (isFirstLoad) {
        setIsFirstLoad(false);
      }
    };

    fetchData();
  }, [fetchTransactions, selectedCreditType, selectedTimeRange, debouncedSearchQuery, currentPage, pageSize]);

  const handlePageChange = (page: number) => {
    setPage(page);
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    // Reset to first page when searching
    if (currentPage !== 1) {
      setPage(1);
    }
  };

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Transactions</h1>
        <p className="text-sm text-muted-foreground">View all your transactions</p>
      </div>
      <div className="container mx-auto py-2">
        {isFirstLoad && isLoading ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading transactions: {error}</div>
        ) : (
          <DataTable 
            columns={columns} 
            data={enrichedTransactions} 
            creditTypes={creditTypes}
            credit_type_id={selectedCreditType}
            onCreditTypeChange={setSelectedCreditType}
            searchQuery={searchQuery}
            onSearchQueryChange={handleSearch}
            timePeriod={selectedTimeRange}
            onTimePeriodChange={setSelectedTimeRange}
            loadingSpinner={isLoading && !isFirstLoad ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            currentPage={currentPage}
            pageSize={pageSize}
            totalCount={totalTransactions}
            onPageChange={handlePageChange}
          />
        )}
      </div>
    </div>
  );
}
