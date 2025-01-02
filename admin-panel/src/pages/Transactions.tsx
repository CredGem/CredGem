import { 
  Input, 
  Table, 
  TableHeader, 
  TableBody, 
  TableColumn, 
  TableRow, 
  TableCell, 
  Chip, 
  Select, 
  SelectItem,
  Card,
  User,
  SortDescriptor,
  Pagination,
  Spinner,
  Button
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { SearchIcon } from "../components/Icons";
import { useEffect, useMemo, useState } from "react";
import { useTransactionStore } from "../store/useTransactionStore";
import { useWalletStore } from "../store/useWalletStore";
import { Transaction, TransactionsQueryParams } from "../types/wallet";

const statusColorMap = {
  deposit: "success",
  debit: "danger",
  adjust: "warning",
} as const;

const timeRanges = [
  { label: "Last 24 Hours", value: "24h" },
  { label: "Last 7 Days", value: "7d" },
  { label: "Last 30 Days", value: "30d" },
  { label: "All Time", value: "all" },
];

export function Transactions() {
  const { 
    transactions, 
    isLoading, 
    error, 
    fetchTransactions,
    totalTransactions,
    currentPage,
    pageSize
  } = useTransactionStore();

  const { creditTypes, fetchCreditTypes, getCreditTypeName } = useWalletStore();

  const [selectedCreditType, setSelectedCreditType] = useState<string>("");
  const [selectedTimeRange, setSelectedTimeRange] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortDescriptor, setSortDescriptor] = useState<SortDescriptor>({
    column: "created_at",
    direction: "descending",
  });

  useEffect(() => {
    if (creditTypes.length === 0) {
      fetchCreditTypes();
    }
  }, [creditTypes.length, fetchCreditTypes]);

  useEffect(() => {
    const fetchData = async () => {
      const params: TransactionsQueryParams = {
        page: currentPage.toString(),
        page_size: pageSize.toString()
      };

      if (selectedCreditType) {
        params.credit_type_id = selectedCreditType;
      }

      // Apply time range filter
      if (selectedTimeRange !== "all") {
        const now = new Date();
        const hours = {
          "24h": 24,
          "7d": 24 * 7,
          "30d": 24 * 30
        }[selectedTimeRange] || 0;

        if (hours) {
          const timeLimit = new Date(now.getTime() - hours * 60 * 60 * 1000);
          params.start_date = timeLimit.toISOString();
        }
      }

      await fetchTransactions(params);
    };

    fetchData();
  }, [fetchTransactions, selectedCreditType, selectedTimeRange, currentPage, pageSize]);

  const sortedItems = useMemo(() => {
    let filteredItems = [...transactions];

    // Apply search filter
    if (searchQuery) {
      filteredItems = filteredItems.filter(item => 
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filteredItems.sort((a, b) => {
      const { column = "created_at", direction = "descending" } = sortDescriptor;
      let first = a[column as keyof Transaction];
      let second = b[column as keyof Transaction];

      if (column === "created_at") {
        first = new Date(a.created_at).getTime();
        second = new Date(b.created_at).getTime();
      }

      const cmp = first < second ? -1 : first > second ? 1 : 0;

      return direction === "descending" ? -cmp : cmp;
    });
  }, [transactions, sortDescriptor, searchQuery]);

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center">
        <p className="text-danger text-large mb-4">{error}</p>
        <Button color="primary" onPress={() => fetchTransactions()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="mt-2 px-12 space-y-8">
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <h3 className="text-sm mb-2">Search Description</h3>
            <Input
              placeholder="Search by description"
              startContent={<SearchIcon />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <div>
            <h3 className="text-sm mb-2">Credit Type</h3>
            <Select
              selectedKeys={selectedCreditType ? [selectedCreditType] : []}
              onChange={(e) => setSelectedCreditType(e.target.value)}
              items={[{ id: "", name: "All Types" }, ...creditTypes]}
            >
              {(type) => (
                <SelectItem key={type.id} value={type.id}>
                  {type.name}
                </SelectItem>
              )}
            </Select>
          </div>

          <div>
            <h3 className="text-sm mb-2">Time Period</h3>
            <Select
              selectedKeys={[selectedTimeRange]}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
            >
              {timeRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center p-8">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <Table 
            aria-label="Transactions table"
            sortDescriptor={sortDescriptor}
            onSortChange={setSortDescriptor}
            bottomContent={
              <div className="flex w-full justify-center">
                <Pagination
                  isCompact
                  showControls
                  showShadow
                  color="primary"
                  page={currentPage}
                  total={Math.ceil(totalTransactions / pageSize)}
                  onChange={(page) => fetchTransactions({ 
                    page: page.toString(), 
                    page_size: pageSize.toString() 
                  })}
                />
              </div>
            }
          >
            <TableHeader>
              <TableColumn key="type" allowsSorting>TYPE</TableColumn>
              <TableColumn key="credit_type_id" allowsSorting>CREDIT TYPE</TableColumn>
              <TableColumn key="description" allowsSorting>DESCRIPTION</TableColumn>
              <TableColumn key="created_at" allowsSorting>DATE</TableColumn>
              <TableColumn key="context">CONTEXT</TableColumn>
            </TableHeader>
            <TableBody>
              {sortedItems.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>
                    <Chip
                      className="capitalize"
                      color={statusColorMap[transaction.type]}
                      size="sm"
                      variant="flat"
                    >
                      {transaction.type}
                    </Chip>
                  </TableCell>
                  <TableCell>{getCreditTypeName(transaction.credit_type_id)}</TableCell>
                  <TableCell>{transaction.description}</TableCell>
                  <TableCell>{new Date(transaction.created_at).toLocaleString()}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(transaction.context).map(([key, value], index) => (
                        <Chip key={index} size="sm" variant="flat">
                          {key}: {value}
                        </Chip>
                      ))}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </div>
  );
} 