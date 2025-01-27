import { WalletDetails } from "@/types/wallet";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wallet as WalletIcon } from "lucide-react";

type WalletHeaderProps = {
  wallet: WalletDetails;
};

export function WalletHeader({ wallet }: WalletHeaderProps) {
  return (
    <div className="flex flex-col relative gap-4 p-4 rounded-lg">
      <h1 className="text-2xl font-bold">Wallet Details</h1>
      <p className="text-sm text-muted-foreground">View wallet details for {wallet.name}</p>
      
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-center gap-3">
            <WalletIcon className="h-10 w-10 text-muted-foreground" />
            <div>
              <p className="font-medium">{wallet.name}</p>
              <p className="text-sm text-muted-foreground">ID: {wallet.id}</p>
            </div>
          </div>
          
          {Object.keys(wallet.context).length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Context</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(wallet.context).map(([key, value], index) => (
                  <Badge key={index} variant="secondary">
                    {key}: {value}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 