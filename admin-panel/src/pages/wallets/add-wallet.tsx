import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Icon } from "@iconify/react";
import { useWalletStore } from "../../store/useWalletStore";
import type { WalletContextPair } from "../../types/wallet";

type AddWalletDialogProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
};

export function AddWalletDialog({ isOpen, onOpenChange }: AddWalletDialogProps) {
  const { createWallet, isLoading } = useWalletStore();
  const [newWalletName, setNewWalletName] = useState("");
  const [contextPairs, setContextPairs] = useState<WalletContextPair[]>([
    { key: "", value: "" },
  ]);

  const handleAddContextPair = () => {
    setContextPairs([...contextPairs, { key: "", value: "" }]);
  };

  const handleRemoveContextPair = (index: number) => {
    setContextPairs(contextPairs.filter((_, i) => i !== index));
  };

  const handleContextPairChange = (
    index: number,
    field: "key" | "value",
    value: string
  ) => {
    const newPairs = [...contextPairs];
    newPairs[index][field] = value;
    setContextPairs(newPairs);
  };

  const handleCreateWallet = async () => {
    const context = contextPairs.reduce((acc, { key, value }) => {
      if (key.trim() && value.trim()) {
        acc[key.trim()] = value.trim();
      }
      return acc;
    }, {} as Record<string, string>);

    await createWallet({
      name: newWalletName,
      context: Object.keys(context).length > 0 ? context : {},
    });

    handleClose();
  };

  const handleClose = () => {
    setNewWalletName("");
    setContextPairs([{ key: "", value: "" }]);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Wallet</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Input
            placeholder="Enter wallet name"
            value={newWalletName}
            onChange={(e) => setNewWalletName(e.target.value)}
          />
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <p className="text-sm font-medium">Context</p>
              <Button
                size="sm"
                variant="outline"
                onClick={handleAddContextPair}
                className="h-8"
              >
                <Icon icon="solar:add-circle-bold" className="mr-2 h-4 w-4" />
                Add Field
              </Button>
            </div>
            {contextPairs.map((pair, index) => (
              <div key={index} className="flex gap-2 items-start">
                <Input
                  className="h-8"
                  placeholder="Enter key"
                  value={pair.key}
                  onChange={(e) =>
                    handleContextPairChange(index, "key", e.target.value)
                  }
                />
                <Input
                  className="h-8"
                  placeholder="Enter value"
                  value={pair.value}
                  onChange={(e) =>
                    handleContextPairChange(index, "value", e.target.value)
                  }
                />
                {contextPairs.length > 1 && (
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8"
                    onClick={() => handleRemoveContextPair(index)}
                  >
                    <Icon
                      icon="solar:trash-bin-trash-bold"
                      className="h-4 w-4"
                    />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateWallet}
            disabled={!newWalletName.trim() || isLoading}
          >
            {isLoading ? "Creating..." : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
