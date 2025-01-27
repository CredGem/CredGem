import React, { useEffect, useState } from "react";
import { useProductStore } from "@/store/useProductStore";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { Skeleton } from "@/components/ui/skeleton";
import { AddProductDialog } from "./add-product";
import { Loader2 } from "lucide-react";

export default function Products() {
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const { 
    products, 
    isLoading, 
    error,
    fetchProducts,
    totalProducts,
    currentPage,
    pageSize,
  } = useProductStore();
  
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchProducts({
      page: currentPage,
      page_size: pageSize,
    }).finally(() => {
      setIsFirstLoad(false);
    });
  }, []);

  const handlePageChange = (page: number) => {
    fetchProducts({
      page,
      page_size: pageSize,
    });
  };

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Products</h1>
        <p className="text-sm text-muted-foreground">Manage your products</p>
      </div>
      <div className="container mx-auto py-2">
        {isLoading && isFirstLoad ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading products: {error}</div>
        ) : (
          <DataTable 
            columns={columns} 
            data={products} 
            onAddProduct={() => setIsOpen(true)}
            currentPage={currentPage}
            pageSize={pageSize}
            totalCount={totalProducts}
            onPageChange={handlePageChange}
            loadingSpinner={isLoading && !isFirstLoad ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          />
        )}
      </div>
      <AddProductDialog
        isOpen={isOpen}
        onOpenChange={setIsOpen}
      />
    </div>
  );
} 