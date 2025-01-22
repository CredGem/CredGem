import { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { Skeleton } from "@/components/ui/skeleton";
import { useTransactionStore } from "@/store/useTransactionStore";
import { Transaction } from "@/types/wallet";
import { toast } from "@/hooks/use-toast";
import { CreditType } from "@/types/creditType";
import { Card, CardContent } from "@/components/ui/card";
import { generateGradientClasses } from "@/components/ui/identiry-card";



const CreditsCard = ({ type }: { type: CreditType }) => {
  return (
    <Card className={`max-w-md`}>
      <CardContent className="pt-6 space-y-4">
        {/* Icon and Title Section */}
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full ${generateGradientClasses(type.id)} flex items-center justify-center`}>
            <span className="text-white text-lg font-medium">r</span>
          </div>
          <div>
            <h2 className="font-medium">regular</h2>
            <p className="text-sm text-muted-foreground">Standard currency credits</p>
          </div>
        </div>

        {/* Dates Section */}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Created</span>
            <span>1/12/2025</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Last Modified</span>
            <span>1/12/2025</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default function Credits() {
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


  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Credits</h1>
        <p className="text-sm text-muted-foreground">View all your credits</p>
      </div>
      <div className="container mx-auto py-2">
        {isLoading ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading wallets: {error}</div>
        ) : (
          <div>
            
            <div className="flex flex-wrap gap-4">
              {creditTypes.map((type) => (
                <CreditsCard key={type.id} type={type} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
