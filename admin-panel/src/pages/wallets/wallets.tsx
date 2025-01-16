import React, { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { Skeleton } from "@/components/ui/skeleton";
import { AddWalletDialog } from "./add-wallet";
import WalletsAnalytics from "./analytics";





export default function Wallets() {
  const { 
    wallets, 
    isLoading, 
    error,
    fetchWallets,
  } = useWalletStore();
  
  const [filterValue, setFilterValue] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  const [isOpen, setIsOpen] = useState(false);


  useEffect(() => {
    fetchWallets({
      page: page,
      page_size: rowsPerPage,
      search: filterValue || undefined
    });
  }, [fetchWallets, page, rowsPerPage, filterValue]);

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Wallets</h1>
        <p className="text-sm text-muted-foreground">View all your wallets</p>
      </div>
      <WalletsAnalytics/>
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
            data={wallets} 
            onAddWallet={() => setIsOpen(true)}
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
