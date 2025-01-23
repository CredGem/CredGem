import { useState, useEffect } from "react";
import { useProductStore } from "@/store/useProductStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Product } from "@/types/product";

interface EditProductDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  product: Product;
}

export function EditProductDialog({ isOpen, onOpenChange, product }: EditProductDialogProps) {
  const [name, setName] = useState(product.name);
  const [description, setDescription] = useState(product.description);

  const { updateProduct, selectedProduct } = useProductStore();
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      setName(product.name);
      setDescription(product.description);
    }
  }, [isOpen, product]);

  const handleUpdate = async () => {
    try {
      // Create an optimistically updated product
      const updatedProduct = {
        ...selectedProduct!,
        name,
        description,
      };

      // Update the store optimistically
      useProductStore.setState({ selectedProduct: updatedProduct });

      // Make the API call
      await updateProduct(product.id, {
        name,
        description,
      });

      toast({
        title: "Success",
        description: "Product updated successfully",
      });
      onOpenChange(false);
    } catch (error) {
      // Revert the optimistic update on error
      useProductStore.setState({ selectedProduct: product });
      toast({
        title: "Error",
        description: "Failed to update product",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Product</DialogTitle>
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
          <Button onClick={handleUpdate} className="w-full">
            Update Product
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
} 