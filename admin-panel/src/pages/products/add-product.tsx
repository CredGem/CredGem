import { useState, useEffect } from "react";
import { useProductStore } from "@/store/useProductStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Icon } from "@iconify/react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CreditType } from "@/types/creditType";
import {useWalletStore} from "@/store/useWalletStore.ts";

interface AddProductDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

interface CreditSettingPair {
  credit_type_id: string;
  credit_amount: number;
}

export function AddProductDialog({ isOpen, onOpenChange }: AddProductDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creditSettings, setCreditSettings] = useState<CreditSettingPair[]>([
    { credit_type_id: "", credit_amount: 0 },
  ]);

  const { createProduct } = useProductStore();
  const { creditTypes, fetchCreditTypes } = useWalletStore();
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      fetchCreditTypes();
    }
  }, [isOpen, fetchCreditTypes]);

  const handleAddCreditSetting = () => {
    setCreditSettings([...creditSettings, { credit_type_id: "", credit_amount: 0 }]);
  };

  const handleRemoveCreditSetting = (index: number) => {
    const newSettings = creditSettings.filter((_, i) => i !== index);
    setCreditSettings(newSettings);
  };

  const handleCreditSettingChange = (
    index: number,
    field: keyof CreditSettingPair,
    value: string | number
  ) => {
    const newSettings = [...creditSettings];
    if (field === "credit_amount") {
      newSettings[index][field] = Number(value);
    } else {
      newSettings[index][field] = value as string;
    }
    setCreditSettings(newSettings);
  };

  const handleCreate = async () => {
    try {
      await createProduct({
        name,
        description,
        settings: creditSettings.map(setting => ({
          credit_type_id: setting.credit_type_id,
          credit_amount: setting.credit_amount,
        })),
      });
      toast({
        title: "Success",
        description: "Product created successfully",
      });
      onOpenChange(false);
      setName("");
      setDescription("");
      setCreditSettings([{ credit_type_id: "", credit_amount: 0 }]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create product",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Product</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              placeholder="Enter product name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              placeholder="Enter product description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label>Credit Settings</Label>
              <Button
                size="sm"
                variant="outline"
                onClick={handleAddCreditSetting}
                className="h-8"
              >
                <Icon icon="solar:add-circle-bold" className="mr-2 h-4 w-4" />
                Add Setting
              </Button>
            </div>
            {creditSettings.map((setting, index) => (
              <div key={index} className="flex gap-2 items-start">
                <div className="flex-1">
                  <Select
                    value={setting.credit_type_id}
                    onValueChange={(value) =>
                      handleCreditSettingChange(index, "credit_type_id", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select credit type" />
                    </SelectTrigger>
                    <SelectContent>
                      {creditTypes.map((type: CreditType) => (
                        <SelectItem key={type.id} value={type.id}>
                          {type.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex-1">
                  <Input
                    type="number"
                    placeholder="Amount"
                    value={setting.credit_amount}
                    onChange={(e) =>
                      handleCreditSettingChange(
                        index,
                        "credit_amount",
                        e.target.value
                      )
                    }
                  />
                </div>
                {creditSettings.length > 1 && (
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8"
                    onClick={() => handleRemoveCreditSetting(index)}
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
          <Button onClick={handleCreate} className="w-full">
            Create Product
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
} 