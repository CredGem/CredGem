import { creditTypeApi } from "@/api/creditTypeApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { useWalletStore } from "@/store/useWalletStore";
import type { CreditType } from "@/types/creditType";
import { WalletIcon, PlusCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import AddCreditsDialog from "./add-credits-dialog";



export default function WalletDetails() {
  const params = useParams();
  const { 
    selectedWallet,
    isLoading, 
    error,
    fetchWallet,
    clearSelectedWallet,
  } = useWalletStore();

  const [creditTypes, setCreditTypes] = useState<Record<string, CreditType>>({});
  const { toast } = useToast();
  
  useEffect(() => {
    if (params.id) {
      fetchWallet(params.id as string);
    }
    return () => {
      clearSelectedWallet();
    };
  }, [params.id, fetchWallet, clearSelectedWallet]);

  useEffect(() => {
    const loadCreditTypes = async () => {
      try {
        const types = await creditTypeApi.getCreditTypes();
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

 
  if (error) {
    return (
      <div className="h-[100vh] flex items-center justify-center">
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => params.id && fetchWallet(params.id as string)}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading || !selectedWallet) {
    return (
      <div className="h-[100vh] flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="h-[100vh] flex flex-col gap-4 p-10">
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Wallet Details</h1>
        <p className="text-sm text-muted-foreground">View wallet details for {selectedWallet.name}</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">General Information</h2>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <WalletIcon className="h-10 w-10 text-muted-foreground" />
              <div>
                <p className="font-medium">{selectedWallet.name}</p>
                <p className="text-sm text-muted-foreground">ID: {selectedWallet.id}</p>
              </div>
            </div>
            
            {Object.keys(selectedWallet.context).length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">Context</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(selectedWallet.context).map(([key, value], index) => (
                    <Badge key={index} variant="secondary">
                      {key}: {value}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
            {/* Balances Overview */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <h2 className="text-xl font-semibold">Balances Overview</h2>
            <AddCreditsDialog />
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Credit Type</TableHead>
                  <TableHead>Available</TableHead>
                  <TableHead>Held</TableHead>
                  <TableHead>Spent</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {selectedWallet.balances.map((balance) => (
                  <TableRow key={balance.credit_type_id}>
                    <TableCell>{creditTypes[balance.credit_type_id]?.name}</TableCell>
                    <TableCell>{balance.available}</TableCell>
                    <TableCell>{balance.held}</TableCell>
                    <TableCell>{balance.spent}</TableCell>
                    <TableCell className="text-right">
                      <AddCreditsDialog 
                        creditTypeId={balance.credit_type_id}
                        trigger={
                          <Button variant="ghost" size="sm">
                            <PlusCircle className="h-4 w-4 mr-2" />
                            Add Credits
                          </Button>
                        }
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
