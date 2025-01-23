import {useEffect, useState} from "react";
import {Button} from "@/components/ui/button";
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,} from "@/components/ui/dialog";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue,} from "@/components/ui/select";
import {useWalletStore} from "@/store/useWalletStore";
import {useProductStore} from "@/store/useProductStore";
import {Loader2} from "lucide-react";
import {Card, CardContent} from "@/components/ui/card";
import {Separator} from "@/components/ui/separator";
import {useToast} from "@/hooks/use-toast";

type SubscriptionType = "ONE_TIME" | "RECURRING";
type SubscriptionMode = "ADD" | "RESET";

interface AddSubscriptionDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  walletId: string;
}

export function AddSubscriptionDialog({ isOpen, onOpenChange, walletId }: AddSubscriptionDialogProps) {
  const [selectedProductId, setSelectedProductId] = useState<string>("");
  const [subscriptionType, setSubscriptionType] = useState<SubscriptionType>("ONE_TIME");
  const [subscriptionMode, setSubscriptionMode] = useState<SubscriptionMode>("ADD");
  const { products, fetchProducts, isLoading: productsLoading, error: productsError } = useProductStore();
  const { subscribeToProduct, isLoading: subscribeLoading, creditTypes, fetchCreditTypes } = useWalletStore();
  const { toast } = useToast();
  const isLoading = productsLoading || subscribeLoading;

  const selectedProduct = products.find(p => p.id === selectedProductId);

  useEffect(() => {
    if (isOpen) {
      fetchProducts();
      fetchCreditTypes();
      setSelectedProductId("");
      setSubscriptionType("ONE_TIME");
      setSubscriptionMode("ADD");
    }
  }, [isOpen, fetchProducts, fetchCreditTypes]);

  const getCreditTypeName = (creditTypeId: string) => {
    const creditType = creditTypes.find(ct => ct.id === creditTypeId);
    return creditType?.name || creditTypeId;
  };

  const handleSubscribe = async () => {
    if (!selectedProductId) return;
    
    try {
      await subscribeToProduct(walletId, { 
        product_id: selectedProductId,
        mode: subscriptionMode,
        type: subscriptionType
      });
      toast({
        title: "Success",
        description: "Successfully subscribed to product",
      });
      onOpenChange(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to subscribe to product",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Subscribe to Product</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {productsError ? (
            <div className="text-sm text-destructive">
              Failed to load products. Please try again.
            </div>
          ) : (
            <>
              <div className="space-y-2">
                <label className="text-sm font-medium">Product</label>
                <Select
                  value={selectedProductId}
                  onValueChange={setSelectedProductId}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={productsLoading ? "Loading products..." : "Select a product"} />
                  </SelectTrigger>
                  <SelectContent>
                    {products.map((product) => (
                      <SelectItem key={product.id} value={product.id}>
                        {product.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedProduct && (
                <Card>
                  <CardContent className="pt-6 space-y-4">
                    <div>
                      <p className="text-sm font-medium">Description</p>
                      <p className="text-sm text-muted-foreground">{selectedProduct.description}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Credit Settings</p>
                      <div className="space-y-2">
                        {selectedProduct.settings.map((setting) => (
                          <div key={setting.id} className="flex justify-between items-center">
                            <span className="text-sm">{getCreditTypeName(setting.credit_type_id)}</span>
                            <span className="text-sm font-medium">{setting.credit_amount} credits</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Separator className="my-2" />

              <div className="space-y-2">
                <label className="text-sm font-medium">Type</label>
                <Select
                  value={subscriptionType}
                  onValueChange={(value: SubscriptionType) => setSubscriptionType(value)}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ONE_TIME">One Time</SelectItem>
                    <SelectItem value="RECURRING">Recurring</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Mode</label>
                <Select
                  value={subscriptionMode}
                  onValueChange={(value: SubscriptionMode) => setSubscriptionMode(value)}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ADD">Add</SelectItem>
                    <SelectItem value="RESET">Reset</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          )}
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubscribe}
            disabled={!selectedProductId || isLoading}
          >
            {subscribeLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Subscribe
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 
