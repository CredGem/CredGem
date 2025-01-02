import React from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Input,
  Button,
  Chip,
  User,
  Pagination,
  Selection,
  ChipProps,
  SortDescriptor,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Textarea,
  Spinner
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { useNavigate } from "react-router-dom";
import { useWalletStore } from "../store/useWalletStore";
import { Wallet, WalletContextPair } from "../types/wallet";

const statusColorMap: Record<string, ChipProps["color"]> = {
  active: "success",
  inactive: "danger",
};

const INITIAL_VISIBLE_COLUMNS = ["name", "status", "context", "lastActivity", "actions"];

export function Wallets() {
  const navigate = useNavigate();
  const { 
    wallets, 
    isLoading, 
    error, 
    totalWallets,
    currentPage,
    pageSize,
    fetchWallets, 
    createWallet, 
    updateWalletStatus 
  } = useWalletStore();
  
  const [filterValue, setFilterValue] = React.useState("");
  const [selectedKeys, setSelectedKeys] = React.useState<Selection>(new Set([]));
  const [visibleColumns, setVisibleColumns] = React.useState<Selection>(new Set(INITIAL_VISIBLE_COLUMNS));
  const [page, setPage] = React.useState(1);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  const [sortDescriptor, setSortDescriptor] = React.useState<SortDescriptor>({
    column: "lastActivity",
    direction: "descending",
  });
  const [isNewWalletOpen, setIsNewWalletOpen] = React.useState(false);
  const [newWalletName, setNewWalletName] = React.useState("");
  const [contextPairs, setContextPairs] = React.useState<WalletContextPair[]>([{ key: '', value: '' }]);

  React.useEffect(() => {
    fetchWallets({
      page: page,
      page_size: rowsPerPage,
      search: filterValue || undefined
    });
  }, [fetchWallets, page, rowsPerPage, filterValue]);

  const hasSearchFilter = Boolean(filterValue);

  const headerColumns = React.useMemo(() => {
    if (visibleColumns === "all") return columns;

    return columns.filter((column) => Array.from(visibleColumns).includes(column.uid));
  }, [visibleColumns]);

  const pages = Math.ceil(totalWallets / rowsPerPage);

  const sortedItems = React.useMemo(() => {
    return [...wallets].sort((a: Wallet, b: Wallet) => {
      const first = a[sortDescriptor.column as keyof Wallet];
      const second = b[sortDescriptor.column as keyof Wallet];
      if (first === undefined || second === undefined) return 0;
      const cmp = first < second ? -1 : first > second ? 1 : 0;

      return sortDescriptor.direction === "descending" ? -cmp : cmp;
    });
  }, [sortDescriptor, wallets]);

  const renderCell = React.useCallback((wallet: Wallet, columnKey: React.Key) => {
    switch (columnKey) {
      case "name":
        return (
          <div className="flex items-center gap-2">
            <Icon icon="solar:building-bold" width={20} height={20} className="text-default-400" />
            <div className="flex flex-col">
              <p className="text-bold text-small">{wallet.name}</p>
              <p className="text-tiny text-default-400">{wallet.id}</p>
            </div>
          </div>
        );
      case "status":
        return (
          <Chip 
            className="capitalize" 
            color={statusColorMap[wallet.status]} 
            size="sm" 
            variant="flat"
            onClick={() => {
              const newStatus = wallet.status === 'active' ? 'inactive' : 'active';
              updateWalletStatus(wallet.id, newStatus);
            }}
          >
            {wallet.status}
          </Chip>
        );
      case "context":
        if (!wallet.context) return null;
        return (
          <div className="flex flex-wrap gap-1">
            {Object.entries(wallet.context).map(([key, value], index) => (
              <Chip key={index} size="sm" variant="flat">
                {key}: {value}
              </Chip>
            ))}
          </div>
        );
      case "lastActivity":
        return (
          <div className="flex flex-col">
            <p className="text-bold text-small capitalize">{new Date(wallet.lastActivity).toLocaleDateString()}</p>
          </div>
        );
      case "actions":
        return (
          <div className="relative flex justify-end items-center gap-2">
            <Button 
              isIconOnly 
              size="sm" 
              variant="light"
              onPress={() => navigate(`/wallets/${wallet.id}`)}
            >
              <Icon icon="solar:eye-bold" width={20} height={20} />
            </Button>
          </div>
        );
      default:
        return wallet[columnKey as keyof Wallet]?.toString() || null;
    }
  }, [navigate, updateWalletStatus]);

  const onNextPage = React.useCallback(() => {
    if (page < pages) {
      setPage(page + 1);
    }
  }, [page, pages]);

  const onPreviousPage = React.useCallback(() => {
    if (page > 1) {
      setPage(page - 1);
    }
  }, [page]);

  const onRowsPerPageChange = React.useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setRowsPerPage(Number(e.target.value));
    setPage(1);
  }, []);

  const onSearchChange = React.useCallback((value?: string) => {
    if (value) {
      setFilterValue(value);
      setPage(1);
    } else {
      setFilterValue("");
    }
  }, []);

  const handleAddContextPair = () => {
    setContextPairs([...contextPairs, { key: '', value: '' }]);
  };

  const handleRemoveContextPair = (index: number) => {
    setContextPairs(contextPairs.filter((_, i) => i !== index));
  };

  const handleContextPairChange = (index: number, field: 'key' | 'value', value: string) => {
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

    const payload = {
      name: newWalletName,
      context: Object.keys(context).length > 0 ? context : {}
    };

    await createWallet(payload);
    setIsNewWalletOpen(false);
    setNewWalletName("");
    setContextPairs([{ key: '', value: '' }]);
  };

  const topContent = React.useMemo(() => {
    return (
      <div className="flex flex-col gap-4">
        <div className="flex justify-between gap-3 items-end">
          <Input
            isClearable
            className="w-full sm:max-w-[44%]"
            placeholder="Search by name..."
            startContent={<Icon icon="solar:magnifer-linear" width={16} height={16} />}
            value={filterValue}
            onClear={() => onSearchChange("")}
            onValueChange={onSearchChange}
          />
          <div className="flex gap-3">
            <Button
              color="primary"
              endContent={<Icon icon="solar:add-circle-bold" width={16} height={16} />}
              onPress={() => setIsNewWalletOpen(true)}
            >
              New Wallet
            </Button>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-default-400 text-small">Total {totalWallets} wallets</span>
          <label className="flex items-center text-default-400 text-small">
            Rows per page:
            <select
              className="bg-transparent outline-none text-default-400 text-small"
              onChange={onRowsPerPageChange}
              value={rowsPerPage}
            >
              <option value="10">10</option>
              <option value="15">15</option>
              <option value="20">20</option>
            </select>
          </label>
        </div>
      </div>
    );
  }, [filterValue, onSearchChange, onRowsPerPageChange, totalWallets, rowsPerPage]);

  const bottomContent = React.useMemo(() => {
    return (
      <div className="py-2 px-2 flex justify-between items-center">
        <Pagination
          isCompact
          showControls
          showShadow
          color="primary"
          page={page}
          total={pages}
          onChange={setPage}
        />
        <div className="hidden sm:flex w-[30%] justify-end gap-2">
          <Button isDisabled={pages === 1} size="sm" variant="flat" onPress={onPreviousPage}>
            Previous
          </Button>
          <Button isDisabled={pages === 1} size="sm" variant="flat" onPress={onNextPage}>
            Next
          </Button>
        </div>
      </div>
    );
  }, [page, pages, onPreviousPage, onNextPage]);

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center">
        <p className="text-danger text-large mb-4">{error}</p>
        <Button color="primary" onPress={() => fetchWallets()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-6">Wallets</h1>
      {isLoading && !wallets.length ? (
        <div className="flex justify-center items-center h-[400px]">
          <Spinner size="lg" />
        </div>
      ) : (
        <Table
          aria-label="Wallets table"
          isHeaderSticky
          bottomContent={bottomContent}
          bottomContentPlacement="outside"
          classNames={{
            wrapper: "max-h-[calc(100vh-300px)]",
            th: "first:pl-2 first:w-[40px]",
            td: "first:pl-2 first:w-[40px]",
          }}
          selectedKeys={selectedKeys}
          selectionMode="multiple"
          sortDescriptor={sortDescriptor}
          topContent={topContent}
          topContentPlacement="outside"
          onSelectionChange={setSelectedKeys}
          onSortChange={setSortDescriptor}
        >
          <TableHeader columns={headerColumns}>
            {(column) => (
              <TableColumn
                key={column.uid}
                align={column.uid === "actions" ? "center" : "start"}
                allowsSorting={column.sortable}
              >
                {column.name}
              </TableColumn>
            )}
          </TableHeader>
          <TableBody emptyContent={"No wallets found"} items={sortedItems}>
            {(item) => (
              <TableRow key={item.id}>
                {(columnKey) => <TableCell>{renderCell(item, columnKey)}</TableCell>}
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}

      <Modal 
        isOpen={isNewWalletOpen} 
        onClose={() => {
          setIsNewWalletOpen(false);
          setNewWalletName("");
          setContextPairs([{ key: '', value: '' }]);
        }}
        size="lg"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Create New Wallet
              </ModalHeader>
              <ModalBody>
                <div className="space-y-4">
                  <Input
                    label="Wallet Name"
                    placeholder="Enter wallet name"
                    value={newWalletName}
                    onChange={(e) => setNewWalletName(e.target.value)}
                  />
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <p className="text-small font-medium">Context</p>
                      <Button
                        size="sm"
                        variant="flat"
                        color="primary"
                        onPress={handleAddContextPair}
                        startContent={<Icon icon="solar:add-circle-bold" width={16} height={16} />}
                      >
                        Add Field
                      </Button>
                    </div>
                    {contextPairs.map((pair, index) => (
                      <div key={index} className="flex gap-2 items-start">
                        <Input
                          size="sm"
                          label="Key"
                          placeholder="Enter key"
                          value={pair.key}
                          onChange={(e) => handleContextPairChange(index, 'key', e.target.value)}
                        />
                        <Input
                          size="sm"
                          label="Value"
                          placeholder="Enter value"
                          value={pair.value}
                          onChange={(e) => handleContextPairChange(index, 'value', e.target.value)}
                        />
                        {contextPairs.length > 1 && (
                          <Button
                            isIconOnly
                            size="sm"
                            variant="light"
                            color="danger"
                            className="mt-7"
                            onPress={() => handleRemoveContextPair(index)}
                          >
                            <Icon icon="solar:trash-bin-trash-bold" width={16} height={16} />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
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
                  onPress={handleCreateWallet}
                  isDisabled={!newWalletName.trim()}
                  isLoading={isLoading}
                >
                  Create
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </div>
  );
}

const columns = [
  {
    name: "NAME",
    uid: "name",
    sortable: true,
  },
  {
    name: "STATUS",
    uid: "status",
    sortable: true,
  },
  {
    name: "CONTEXT",
    uid: "context",
    sortable: false,
  },
  {
    name: "LAST ACTIVITY",
    uid: "lastActivity",
    sortable: true,
  },
  {
    name: "ACTIONS",
    uid: "actions",
  },
]; 