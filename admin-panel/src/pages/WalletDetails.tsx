import React from "react";
import { 
  Button, 
  Card, 
  Chip, 
  Table, 
  TableHeader, 
  TableColumn, 
  TableBody, 
  TableRow, 
  TableCell,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Input,
  ButtonGroup,
  Spinner
} from "@nextui-org/react";
import { useNavigate, useParams } from "react-router-dom";
import { Icon } from "@iconify/react";
import { useWalletStore } from "../store/useWalletStore";
import { WalletBalance, WalletContextPair } from "../types/wallet";
import { KeyValuePairsInput } from "../components/KeyValuePairsInput";

export function WalletDetails() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { 
    selectedWallet, 
    isLoading, 
    error, 
    fetchWallet, 
    clearSelectedWallet,
    creditTypes,
    fetchCreditTypes,
    getCreditTypeName,
    processCredits
  } = useWalletStore();

  const [selectedBalance, setSelectedBalance] = React.useState<WalletBalance | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = React.useState(false);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = React.useState(false);
  const [isResetModalOpen, setIsResetModalOpen] = React.useState(false);
  const [creditAmount, setCreditAmount] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [issuer, setIssuer] = React.useState("");
  const [contextPairs, setContextPairs] = React.useState<WalletContextPair[]>([{ key: '', value: '' }]);
  const [resetSpent, setResetSpent] = React.useState(false);

  React.useEffect(() => {
    if (id) {
      fetchWallet(id);
    }
    return () => {
      clearSelectedWallet();
    };
  }, [id, fetchWallet, clearSelectedWallet]);

  React.useEffect(() => {
    if (creditTypes.length === 0) {
      fetchCreditTypes();
    }
  }, [creditTypes.length, fetchCreditTypes]);

  const handleQuickAdd = (amount: number) => {
    setCreditAmount(amount.toString());
  };

  const getNewBalance = () => {
    if (!selectedBalance || !creditAmount) return selectedBalance?.available || 0;
    const newBalance = isAddModalOpen 
      ? selectedBalance.available + Number(creditAmount)
      : selectedBalance.available - Number(creditAmount);
    return newBalance;
  };

  const hasBalanceChanged = () => {
    if (!selectedBalance || !creditAmount) return false;
    const newBalance = getNewBalance();
    return newBalance !== selectedBalance.available;
  };

  const handleAction = async () => {
    if (!selectedWallet?.id || !selectedBalance?.credit_type_id || !issuer.trim()) return;
    if (!creditAmount) return;

    const context = contextPairs.reduce((acc, { key, value }) => {
      if (key.trim() && value.trim()) {
        acc[key.trim()] = value.trim();
      }
      return acc;
    }, {} as Record<string, string>);

    try {
      const type = isAddModalOpen ? 'deposit' : isRemoveModalOpen ? 'debit' : 'adjust';
      await processCredits(
        type,
        selectedWallet.id,
        selectedBalance.credit_type_id,
        Number(creditAmount),
        description,
        issuer.trim(),
        Object.keys(context).length > 0 ? context : undefined,
        isResetModalOpen ? resetSpent : undefined
      );
      setIsAddModalOpen(false);
      setIsRemoveModalOpen(false);
      setIsResetModalOpen(false);
      setCreditAmount("");
      setDescription("");
      setIssuer("");
      setContextPairs([{ key: '', value: '' }]);
      setResetSpent(false);
      setSelectedBalance(null);
    } catch (error) {
      console.error('Failed to process credits:', error);
    }
  };

  const renderActionButtons = (balance: WalletBalance) => (
    <div className="flex gap-2">
      <Button 
        size="sm" 
        variant="flat"
        color="success"
        onPress={() => {
          setSelectedBalance(balance);
          setIsAddModalOpen(true);
        }}
      >
        Add Credits
      </Button>
      <Button 
        size="sm" 
        variant="flat"
        color="danger"
        onPress={() => {
          setSelectedBalance(balance);
          setIsRemoveModalOpen(true);
        }}
      >
        Remove Credits
      </Button>
      <Button 
        size="sm" 
        variant="flat"
        onPress={() => {
          setSelectedBalance(balance);
          setIsResetModalOpen(true);
        }}
      >
        Reset
      </Button>
    </div>
  );

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center">
        <p className="text-danger text-large mb-4">{error}</p>
        <Button color="primary" onPress={() => id && fetchWallet(id)}>
          Retry
        </Button>
      </div>
    );
  }

  if (isLoading || !selectedWallet) {
    return (
      <div className="p-8 flex justify-center items-center h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center gap-4 mb-6">
        <Button 
          variant="light" 
          onPress={() => navigate('/wallets')}
          startContent={<span className="text-xl">←</span>}
        >
          Back to Wallets
        </Button>
        <h1 className="text-4xl font-bold">Wallet Details</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">General Information</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Icon icon="solar:building-bold" width={40} height={40} className="text-default-400" />
              <div>
                <p className="text-medium font-semibold">{selectedWallet.name}</p>
                <p className="text-small text-default-400">ID: {selectedWallet.id}</p>
              </div>
            </div>
            <div>
              <p className="text-small text-default-500">Created At</p>
              <p className="text-medium">{new Date(selectedWallet.created_at).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-small text-default-500">Last Updated</p>
              <p className="text-medium">{new Date(selectedWallet.updated_at).toLocaleString()}</p>
            </div>
            {Object.keys(selectedWallet.context).length > 0 && (
              <div>
                <p className="text-small text-default-500 mb-2">Context</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(selectedWallet.context).map(([key, value], index) => (
                    <Chip key={index} size="sm" variant="flat">
                      {key}: {value}
                    </Chip>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Balances Overview</h2>
          <div className="space-y-4">
            {selectedWallet.balances.map((balance) => (
              <div key={balance.id} className="flex justify-between items-center p-3 bg-default-100 rounded-lg">
                <div>
                  <p className="text-small">{getCreditTypeName(balance.credit_type_id)}</p>
                  <p className="text-tiny text-default-500">Available: {balance.available}</p>
                </div>
                <div className="text-right">
                  <p className="text-small">Spent: {balance.overall_spent}</p>
                  <p className="text-tiny text-default-500">Held: {balance.held}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Detailed Balances</h2>
          <Table aria-label="Credit balances table">
            <TableHeader>
              <TableColumn>CREDIT TYPE</TableColumn>
              <TableColumn>AVAILABLE</TableColumn>
              <TableColumn>HELD</TableColumn>
              <TableColumn>SPENT</TableColumn>
              <TableColumn>OVERALL SPENT</TableColumn>
              <TableColumn>ACTIONS</TableColumn>
            </TableHeader>
            <TableBody>
              {selectedWallet.balances.map((balance) => (
                <TableRow key={balance.id}>
                  <TableCell>{getCreditTypeName(balance.credit_type_id)}</TableCell>
                  <TableCell>{balance.available}</TableCell>
                  <TableCell>{balance.held}</TableCell>
                  <TableCell>{balance.spent}</TableCell>
                  <TableCell>{balance.overall_spent}</TableCell>
                  <TableCell>
                    {renderActionButtons(balance)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

      <Modal 
        isOpen={isAddModalOpen || isRemoveModalOpen || isResetModalOpen} 
        onClose={() => {
          setIsAddModalOpen(false);
          setIsRemoveModalOpen(false);
          setIsResetModalOpen(false);
          setCreditAmount("");
          setDescription("");
          setIssuer("");
          setContextPairs([{ key: '', value: '' }]);
          setResetSpent(false);
          setSelectedBalance(null);
        }}
        size="lg"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                {isAddModalOpen ? "Add Credits" : isRemoveModalOpen ? "Remove Credits" : "Reset Credits"}
              </ModalHeader>
              <ModalBody>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-default-500">Current Balance:</span>
                    <span className="font-semibold">{selectedBalance?.available}</span>
                  </div>
                  
                  {isAddModalOpen && (
                    <div className="flex flex-wrap gap-2">
                      <span className="w-full text-small text-default-500">Quick Add:</span>
                      <ButtonGroup>
                        <Button variant="flat" onPress={() => handleQuickAdd(100)}>+100</Button>
                        <Button variant="flat" onPress={() => handleQuickAdd(200)}>+200</Button>
                        <Button variant="flat" onPress={() => handleQuickAdd(500)}>+500</Button>
                        <Button variant="flat" onPress={() => handleQuickAdd(1000)}>+1000</Button>
                      </ButtonGroup>
                    </div>
                  )}

                  {!isResetModalOpen && (
                    <Input
                      label={`${isAddModalOpen ? 'Add' : 'Remove'} Amount`}
                      placeholder="Enter amount"
                      type="number"
                      value={creditAmount}
                      onChange={(e) => setCreditAmount(e.target.value)}
                    />
                  )}

                  <Input
                    label="Description"
                    placeholder="Enter description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />

                  <Input
                    label="Issuer"
                    placeholder="Enter issuer"
                    value={issuer}
                    onChange={(e) => setIssuer(e.target.value)}
                    isRequired
                  />

                  {isResetModalOpen && (
                    <>
                      <Input
                        label="Reset Amount"
                        placeholder="Enter amount to reset to"
                        type="number"
                        value={creditAmount}
                        onChange={(e) => setCreditAmount(e.target.value)}
                      />
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="resetSpent"
                          checked={resetSpent}
                          onChange={(e) => setResetSpent(e.target.checked)}
                        />
                        <label htmlFor="resetSpent">Reset Spent Amount</label>
                      </div>
                    </>
                  )}

                  <KeyValuePairsInput
                    pairs={contextPairs}
                    onChange={setContextPairs}
                    label="Transaction Context"
                  />

                  {!isResetModalOpen && (
                    <div className="flex justify-between items-center">
                      <span className="text-default-500">New Balance:</span>
                      <span className="font-semibold">{getNewBalance()}</span>
                    </div>
                  )}

                  {isResetModalOpen && creditAmount && (
                    <div className="flex justify-between items-center">
                      <span className="text-default-500">Will Reset Balance To:</span>
                      <span className="font-semibold">{Number(creditAmount)}</span>
                    </div>
                  )}
                </div>
              </ModalBody>
              <ModalFooter>
                <Button 
                  variant="light" 
                  onPress={onClose}
                >
                  Cancel
                </Button>
                <Button 
                  color="primary"
                  onPress={handleAction}
                  isDisabled={
                    !issuer.trim() || 
                    !creditAmount ||
                    (!isResetModalOpen && (Number(creditAmount) <= 0 || !hasBalanceChanged()))
                  }
                >
                  Approve
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </div>
  );
} 