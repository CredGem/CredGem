import {creditTypeApi} from "@/api/creditTypeApi";
import {Button} from "@/components/ui/button";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {useToast} from "@/hooks/use-toast";
import {useWalletStore} from "@/store/useWalletStore";
import {Plus} from "lucide-react";
import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import {WalletHeader} from "./wallet-header";
import {WalletBalances} from "./wallet-balances";
import {WalletTransactions} from "./wallet-transactions";
import {SubscriptionsSection} from "./subscriptions-section";
import {AddSubscriptionDialog} from "./add-subscription-dialog";

export default function WalletDetails() {
  const { id } = useParams<{ id: string }>();
  const { selectedWallet, fetchWallet, isLoading, error } = useWalletStore();
  const { toast } = useToast();
  const [isAddSubscriptionOpen, setIsAddSubscriptionOpen] = useState(false);

  useEffect(() => {
    if (id) {
      fetchWallet(id);
    }
  }, [id, fetchWallet]);

  useEffect(() => {
    const loadCreditTypes = async () => {
      try {
        const types = await creditTypeApi.getCreditTypes();
        const creditTypesRes = {};
        types.forEach((type) => {
            creditTypesRes[type.id] = type;
        });
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

  if (!id) return null;

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!selectedWallet) {
    return <div>Wallet not found</div>;
  }

  return (
    <div className="container mx-auto py-6 space-y-8">
      <WalletHeader wallet={selectedWallet} />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <WalletBalances wallet={selectedWallet} />
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-2xl font-bold">Subscriptions</CardTitle>
            <Button onClick={() => setIsAddSubscriptionOpen(true)} variant="outline" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Subscription
            </Button>
          </CardHeader>
          <CardContent>
            <SubscriptionsSection walletId={id} />
          </CardContent>
        </Card>
      </div>
      <WalletTransactions walletId={id} />
      <AddSubscriptionDialog
        isOpen={isAddSubscriptionOpen}
        onOpenChange={setIsAddSubscriptionOpen}
        walletId={id}
      />
    </div>
  );
}
