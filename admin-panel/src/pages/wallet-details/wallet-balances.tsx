import { WalletDetails } from "@/types/wallet";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import { useWalletStore } from "@/store/useWalletStore";
import AddCreditsDialog from "./add-credits-dialog";

type WalletBalancesProps = {
  wallet: WalletDetails;
};

export function WalletBalances({ wallet }: WalletBalancesProps) {
  const { creditTypes } = useWalletStore();

  return (
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
              {wallet.balances.map((balance) => (
                <TableRow key={balance.credit_type_id}>
                  <TableCell>{creditTypes.find(ct => ct.id === balance.credit_type_id)?.name}</TableCell>
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
  );
} 