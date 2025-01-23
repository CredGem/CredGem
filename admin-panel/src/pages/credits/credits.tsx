import { useEffect, useState } from "react";
import { useWalletStore } from "@/store/useWalletStore";
import { Skeleton } from "@/components/ui/skeleton";
import { useTransactionStore } from "@/store/useTransactionStore";
import { Transaction } from "@/types/wallet";
import { toast } from "@/hooks/use-toast";
import { CreditType } from "@/types/creditType";
import { Card, CardContent } from "@/components/ui/card";
import { generateGradientClasses } from "@/components/ui/identiry-card";
import { Button } from "@/components/ui/button";
import { EditCreditDialog } from "./edit-credit-dialog";
import { AddCreditDialog } from "./add-credit-dialog";
import { formatDate } from "@/lib/utils";
import { Pencil, Plus } from "lucide-react";

const CreditsCard = ({ type }: { type: CreditType }) => {
  const [isEditOpen, setIsEditOpen] = useState(false);

  return (
    <>
      <Card className="w-[350px] h-[200px]">
        <CardContent className="pt-6 space-y-4 h-full flex flex-col">
          {/* Icon and Title Section */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full ${generateGradientClasses(type.id)} flex items-center justify-center`}>
                <span className="text-white text-lg font-medium">{type.name[0]}</span>
              </div>
              <div>
                <h2 className="font-medium">{type.name}</h2>
                <p className="text-sm text-muted-foreground line-clamp-2">{type.description}</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setIsEditOpen(true)}>
              <Pencil className="h-4 w-4" />
            </Button>
          </div>

          {/* Dates Section */}
          <div className="space-y-2 text-sm mt-auto">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{formatDate(type.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Last Modified</span>
              <span>{formatDate(type.updated_at)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
      <EditCreditDialog
        isOpen={isEditOpen}
        onOpenChange={setIsEditOpen}
        creditType={type}
      />
    </>
  );
};

export default function Credits() {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const { 
    creditTypes, 
    fetchCreditTypes,
    isLoading,
    error
  } = useWalletStore();

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

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Credits</h1>
            <p className="text-sm text-muted-foreground">View all your credits</p>
          </div>
          <Button onClick={() => setIsAddOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Credit Type
          </Button>
        </div>
      </div>
      <div className="container mx-auto py-2">
        {isLoading ? (
          <div className="w-full h-48 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : error ? (
          <div className="text-red-500">Error loading credit types: {error}</div>
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
      <AddCreditDialog isOpen={isAddOpen} onOpenChange={setIsAddOpen} />
    </div>
  )
}
