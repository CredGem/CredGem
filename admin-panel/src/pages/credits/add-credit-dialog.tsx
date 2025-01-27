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
import { Textarea } from "@/components/ui/textarea";

type AddCreditDialogProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
};

export function AddCreditDialog({ isOpen, onOpenChange }: AddCreditDialogProps) {
  const { createCreditType, isLoading } = useWalletStore();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const handleCreateCreditType = async () => {
    try {
      await createCreditType({
        name,
        description,
      });
      handleClose();
    } catch (error) {
      // Error is handled by the store
    }
  };

  const handleClose = () => {
    setName("");
    setDescription("");
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Credit Type</DialogTitle>
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
            onClick={handleCreateCreditType}
            disabled={!name.trim() || !description.trim() || isLoading}
          >
            {isLoading ? "Creating..." : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 