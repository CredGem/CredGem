import { useEffect, useState } from "react";
import { useWalletStore } from "../store/useWalletStore";
import { CreditType } from "../types/creditType";
import { DotsVerticalIcon } from "../components/Icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Dialog, DialogFooter, DialogHeader } from "@/components/ui/dialog";
import { DialogContent } from "@/components/ui/dialog";

// Function to generate a color based on string
const stringToColor = (str: string) => {
  // Predefined vibrant colors
  const colors = [
    '#9353D3',  // Vibrant purple
    '#0072F5',  // Bright blue
    '#17C964',  // Bright green
    '#F5A524',  // Bright orange
    '#FF4ECD',  // Pink
    '#4B4EFF',  // Indigo
    '#FF4E4E',  // Red
    '#00B8D9',  // Cyan
    '#36B37E',  // Green
    '#FF8B00',  // Orange
    '#998DD9',  // Light purple
    '#E95800',  // Burnt orange
  ];

  // Generate a consistent index based on the string
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Use the hash to select a color
  const index = Math.abs(hash) % colors.length;
  return colors[index];
};

// Function to generate gradient style
const getGradientStyle = (name: string) => {
  const color = stringToColor(name);
  return {
    background: `linear-gradient(135deg, ${color}44 0%, ${color} 100%)`,
    width: "48px",
    height: "48px",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "white",
    fontSize: "1.5rem",
    fontWeight: "500",
    marginBottom: "1rem",
    boxShadow: `0 4px 14px 0 ${color}33`
  };
};

export function CreditSettings() {
  const { 
    creditTypes, 
    isLoading, 
    error, 
    fetchCreditTypes,
    createCreditType,
    updateCreditType,
    deleteCreditType
  } = useWalletStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCreditType, setSelectedCreditType] = useState<CreditType | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  useEffect(() => {
    fetchCreditTypes();
  }, [fetchCreditTypes]);

  const handleCreate = async () => {
    await createCreditType(formData);
    setIsCreateModalOpen(false);
    setFormData({ name: '', description: '' });
  };

  const handleEdit = async () => {
    if (!selectedCreditType) return;
    await updateCreditType(selectedCreditType.id, formData);
    setIsEditModalOpen(false);
    setSelectedCreditType(null);
    setFormData({ name: '', description: '' });
  };

  const handleDelete = async () => {
    if (!selectedCreditType) return;
    await deleteCreditType(selectedCreditType.id);
    setIsDeleteModalOpen(false);
    setSelectedCreditType(null);
  };

  const openEditModal = (creditType: CreditType) => {
    setSelectedCreditType(creditType);
    setFormData({
      name: creditType.name,
      description: creditType.description
    });
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (creditType: CreditType) => {
    setSelectedCreditType(creditType);
    setIsDeleteModalOpen(true);
  };

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center">
        <p className="text-danger text-large mb-4">{error}</p>
        <Button color="primary" onClick={fetchCreditTypes}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="mt-2 px-12 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Credit Settings</h1>
          <p className="text-small text-default-500">Manage your credit types and units</p>
        </div>
        <Button 
          color="primary"
          onClick={() => {
            setFormData({ name: '', description: '' });
            setIsCreateModalOpen(true);
          }}
        >
          Create New Credit Type
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center p-8">
          <p>Loading...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {creditTypes.map((creditType) => (
            <Card key={creditType.id} className="p-4">
              <div className="flex flex-col">
                <div style={getGradientStyle(creditType.name)}>
                  {creditType.name.charAt(0)}
                </div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold">{creditType.name}</h3>
                    <p className="text-small text-default-500">{creditType.description}</p>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <Button 
                        size="sm" 
                        variant="outline"
                      >
                        <DotsVerticalIcon />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => openEditModal(creditType)}>
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-danger" 
                        color="danger"
                        onClick={() => openDeleteModal(creditType)}
                      >
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <div className="mt-4 pt-4 border-t border-divider">
                  <div className="grid grid-cols-2 gap-2 text-small">
                    <div className="text-default-500">Created</div>
                    <div>{new Date(creditType.created_at).toLocaleDateString()}</div>
                    <div className="text-default-500">Last Modified</div>
                    <div>{new Date(creditType.updated_at).toLocaleDateString()}</div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Dialog 
        open={isCreateModalOpen} 
        onOpenChange={setIsCreateModalOpen}
      >
        <DialogContent>
          <DialogHeader className="flex flex-col gap-1">
            Create Credit Type
          </DialogHeader>
          <DialogContent>
            <Input
              placeholder="Enter credit type name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
            />
            <Textarea
              placeholder="Enter credit type description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
          </DialogContent>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
                </Button>
                <Button 
              color="primary"
              onClick={handleCreate}
              disabled={!formData.name.trim()}
            >
              Create
              </Button>
            </DialogFooter>
          </DialogContent>
      </Dialog>

      {/* Edit Modal */}
        <Dialog 
        open={isEditModalOpen} 
        onOpenChange={setIsEditModalOpen}
      >
          <DialogHeader className="flex flex-col gap-1">
            Edit Credit Type
          </DialogHeader>
          <DialogContent>
            <Input
              placeholder="Enter credit type name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
            />
            <Textarea
              placeholder="Enter credit type description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              required
            />
              </DialogContent>
              <DialogFooter>
                <Button 
                  variant="outline" 
                  onClick={() => setIsEditModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  color="primary"
                  onClick={handleEdit}
                  disabled={!formData.name.trim()}
                >
                  Save Changes
                </Button>
            </DialogFooter>
      </Dialog>

      {/* Delete Modal */}
      <Dialog 
        open={isDeleteModalOpen} 
        onOpenChange={setIsDeleteModalOpen}
      >
      
      <DialogHeader className="flex flex-col gap-1">
                Delete Credit Type
              </DialogHeader>
        <DialogContent>
              <DialogContent>
                <p>
                  Are you sure you want to delete the credit type "{selectedCreditType?.name}"? 
                  This action cannot be undone.
                </p>
              </DialogContent>
              <DialogFooter>
                <Button 
                  variant="outline" 
                  onClick={() => setIsDeleteModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  color="danger"
                  onClick={handleDelete}
                >
                  Delete
                </Button>
              </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 