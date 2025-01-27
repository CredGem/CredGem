import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { useProductStore } from "@/store/useProductStore";
import { useWalletStore } from "@/store/useWalletStore";
import { Package, Pencil } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { EditProductDialog } from "./edit-product-dialog";

export default function ProductDetails() {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const params = useParams();
  const { 
    selectedProduct,
    isLoading, 
    error,
    fetchProduct,
    clearSelectedProduct,
  } = useProductStore();

  const { creditTypes, fetchCreditTypes } = useWalletStore();
  const { toast } = useToast();
  
  useEffect(() => {
    if (params.id) {
      fetchProduct(params.id as string);
      fetchCreditTypes();
    }
    return () => {
      clearSelectedProduct();
    };
  }, [params.id, fetchProduct, clearSelectedProduct, fetchCreditTypes]);

  if (error) {
    return (
      <div className="h-[100vh] flex items-center justify-center">
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => params.id && fetchProduct(params.id as string)}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading || !selectedProduct) {
    return (
      <div className="h-[100vh] flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="h-[100vh] flex flex-col gap-4 p-10">
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg`}>
        <h1 className="text-2xl font-bold">Product Details</h1>
        <p className="text-sm text-muted-foreground">View product details for {selectedProduct.name}</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <h2 className="text-xl font-semibold">General Information</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditDialogOpen(true)}
            >
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <Package className="h-10 w-10 text-muted-foreground" />
              <div>
                <p className="font-medium">{selectedProduct.name}</p>
                <p className="text-sm text-muted-foreground">ID: {selectedProduct.id}</p>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-muted-foreground mb-2">Description</p>
              <p>{selectedProduct.description}</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-2">Status</p>
              <Badge variant={selectedProduct.status === "ACTIVE" ? "default" : "secondary"}>
                {selectedProduct.status}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Credit Settings */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Credit Settings</h2>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Credit Type</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Created At</TableHead>
                    <TableHead>Updated At</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedProduct.settings.map((setting) => {
                    const creditType = creditTypes.find(type => type.id === setting.credit_type_id);
                    return (
                      <TableRow key={setting.id}>
                        <TableCell>{creditType?.name}</TableCell>
                        <TableCell>{setting.credit_amount}</TableCell>
                        <TableCell>{new Date(setting.created_at).toLocaleDateString()}</TableCell>
                        <TableCell>{new Date(setting.updated_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      <EditProductDialog 
        isOpen={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        product={selectedProduct}
      />
    </div>
  );
} 