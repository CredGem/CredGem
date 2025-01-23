import React, { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { Skeleton } from "@/components/ui/skeleton";
import { AddWalletDialog } from "./add-wallet";
import WalletsAnalytics from "./analytics";
import { Loader2 } from "lucide-react";
import { useDebounce } from "@/lib/utils";

export default function Wallets() {
  const { 
    wallets, 
    isLoading, 
    error,
    fetchWallets,
    totalWallets,
    currentPage,
    pageSize,
    setPage
  } = useWalletStore();
  
  const [filterValue, setFilterValue] = React.useState("");
  const debouncedFilterValue = useDebounce(filterValue, 500); // 500ms delay
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      await fetchWallets({
        page: currentPage,
        page_size: pageSize,
        search: debouncedFilterValue || undefined
      });
      if (isFirstLoad) {
        setIsFirstLoad(false);
      }
    };

    fetchData();
  }, [fetchWallets, currentPage, pageSize, debouncedFilterValue]);

  const handlePageChange = (page: number) => {
    setPage(page);
  };

  const handleSearch = (value: string) => {
    setFilterValue(value);
    // Reset to first page when searching
    if (currentPage !== 1) {
      setPage(1);
    }
  };

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Wallets</h1>
        <p className="text-sm text-muted-foreground">View all your wallets</p>
      </div>
      <WalletsAnalytics/>
      <div className="container mx-auto py-2">
        {isFirstLoad && isLoading ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading wallets: {error}</div>
        ) : (
          <DataTable 
            columns={columns} 
            data={wallets} 
            onAddWallet={() => setIsOpen(true)}
            currentPage={currentPage}
            pageSize={pageSize}
            totalCount={totalWallets}
            onPageChange={handlePageChange}
            loadingSpinner={isLoading && !isFirstLoad ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            searchQuery={filterValue}
            onSearchQueryChange={handleSearch}
          />
        )}
      </div>
      <AddWalletDialog
        isOpen={isOpen}
        onOpenChange={setIsOpen}
      />
    </div>
  )
}
