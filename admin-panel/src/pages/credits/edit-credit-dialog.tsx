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
import { useWalletStore } from "@/store/useWalletStore";
import { CreditType } from "@/types/creditType";
import { Textarea } from "@/components/ui/textarea";

type EditCreditDialogProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  creditType: CreditType;
};

export function EditCreditDialog({ isOpen, onOpenChange, creditType }: EditCreditDialogProps) {
  const { updateCreditType, isLoading } = useWalletStore();
  const [name, setName] = useState(creditType.name);
  const [description, setDescription] = useState(creditType.description);

  const handleUpdateCreditType = async () => {
    try {
      await updateCreditType(creditType.id, {
        name,
        description,
      });
      handleClose();
    } catch (error) {
      // Error is handled by the store
    }
  };

  const handleClose = () => {
    setName(creditType.name);
    setDescription(creditType.description);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Credit Type</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Name</label>
            <Input
              placeholder="Enter credit type name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <Textarea
              placeholder="Enter credit type description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleUpdateCreditType}
            disabled={!name.trim() || !description.trim() || isLoading}
          >
            {isLoading ? "Updating..." : "Update"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 