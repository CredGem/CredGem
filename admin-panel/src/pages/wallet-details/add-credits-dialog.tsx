import { creditTypeApi } from "@/api/creditTypeApi";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useWalletStore } from "@/store/useWalletStore";
import type { CreditType } from "@/types/creditType";
import { PlusCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
type WalletAction = 'deposit' | 'debit' | 'adjust';

type AddCreditsDialogProps = {
  creditTypeId?: string;
  trigger?: React.ReactNode;
}

export default function AddCreditsDialog({ creditTypeId, trigger }: AddCreditsDialogProps) {
  const [amount, setAmount] = useState("");
  const [selectedCreditType, setSelectedCreditType] = useState<string>(creditTypeId || "");
  const [isAddingCreditType, setIsAddingCreditType] = useState(false);
  const [newCreditType, setNewCreditType] = useState("");
  const [selectedAction, setSelectedAction] = useState<WalletAction>('deposit');
  const [resetSpent, setResetSpent] = useState(false);
  const { toast } = useToast();
  const [issuer, setIssuer] = useState("");
  const [description, setDescription] = useState("");
  const location = useLocation()
  const navigate = useNavigate()
  const walletId = location.pathname.split("/").pop()
  if (!walletId) { navigate("/wallets") }
  const {
    creditTypes,
    processCredits,
    fetchCreditTypes
  } = useWalletStore();

  const handleActionSubmit = async () => {
    if (!walletId) { return }
    try {

      switch (selectedAction) {
        case 'deposit':
          await processCredits('deposit', walletId, selectedCreditType, Number(amount), description, issuer, {}, false);
          break;
        case 'debit':
          await processCredits('debit', walletId, selectedCreditType, Number(amount), description, issuer, {}, false);
          break;
        case 'adjust':
          await processCredits('adjust', walletId, selectedCreditType, Number(amount), description, issuer, {}, resetSpent);
          break;
      }

      toast({
        title: "Action completed successfully",
        description: `${selectedAction.charAt(0).toUpperCase() + selectedAction.slice(1)}ed ${amount} credits of type ${selectedCreditType}`,
      });

      setAmount("");
      setSelectedCreditType("");

    } catch (error) {
      toast({
        title: "Error performing action",
        description: `Failed to ${selectedAction} credits`,
        variant: "destructive",
      });
    }
  };

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
    <Dialog>
      <DialogTrigger asChild>
        {trigger || <Button>Add Credits</Button>}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage Wallet Credits</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Action</Label>
            <Select value={selectedAction} onValueChange={(value: WalletAction) => setSelectedAction(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="deposit">Deposit</SelectItem>
                <SelectItem value="debit">Debit</SelectItem>
                <SelectItem value="adjust">Adjust</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Credit Type</Label>
            <div className="flex gap-2">
              <Select value={selectedCreditType} onValueChange={setSelectedCreditType}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Select credit type" />
                </SelectTrigger>
                <SelectContent>
                  {creditTypes.map((type) => (
                    <SelectItem key={type.id} value={type.id}>
                      {type.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                onClick={() => setIsAddingCreditType(true)}
              >
                New Type
              </Button>
            </div>
          </div>

          {isAddingCreditType && (
            <div className="space-y-2">
              <Label>New Credit Type</Label>
              <div className="flex flex-col gap-2">
                <Input
                  value={newCreditType}
                  onChange={(e) => setNewCreditType(e.target.value)}
                  placeholder="Enter credit type name"
                />
                <Button
                  variant="secondary"
                  onClick={async () => {
                    try {
                      const newType = await creditTypeApi.createCreditType(newCreditType, "");
                      await fetchCreditTypes();
                      setSelectedCreditType(newType.id);
                      setIsAddingCreditType(false);
                      setNewCreditType("");
                    } catch (error) {
                      toast({
                        title: "Error creating credit type",
                        description: "Failed to create new credit type",
                        variant: "destructive",
                      });
                    }
                  }}
                >
                  Add Credit Type
                </Button>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label>Amount</Label>
            <Input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Enter amount"
            />
          </div>

          {selectedAction === 'adjust' && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="resetSpent"
                checked={resetSpent}
                onChange={(e) => setResetSpent(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="resetSpent">Reset Spent Amount</Label>
            </div>
          )}

          <div className="space-y-2">
            <Label>Issuer</Label>
            <Input
              value={issuer}
              onChange={(e) => setIssuer(e.target.value)}
              placeholder="Enter issuer"
            />
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter description"
            />
          </div>

          <Button
            onClick={handleActionSubmit}
            className="w-full"
            disabled={!selectedCreditType || !amount || !selectedAction}
          >
            {selectedAction.charAt(0).toUpperCase() + selectedAction.slice(1)} Credits
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}