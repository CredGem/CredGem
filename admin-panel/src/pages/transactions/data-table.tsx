import {Button} from "@/components/ui/button"

import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
    SortingState,
    getSortedRowModel,
    getFilteredRowModel,
    ColumnFiltersState,
} from "@tanstack/react-table"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {useState} from "react"
import {Input} from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {CreditType} from "@/types/creditType"

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
    creditTypes: CreditType[]
    credit_type_id: string | undefined
    onCreditTypeChange: (value: string | undefined) => void
    searchQuery: string
    onSearchQueryChange: (value: string) => void
    timePeriod: string
    onTimePeriodChange: (value: string) => void
    loadingSpinner?: React.ReactNode
    currentPage: number
    pageSize: number
    totalCount: number
    onPageChange: (page: number) => void
}

export function DataTable<TData, TValue>({
                                             columns,
                                             data,
                                             creditTypes,
                                             credit_type_id,
                                             onCreditTypeChange,
                                             searchQuery,
                                             onSearchQueryChange,
                                             timePeriod,
                                             onTimePeriodChange,
                                             loadingSpinner,
                                             currentPage,
                                             pageSize,
                                             totalCount,
                                             onPageChange,
                                         }: DataTableProps<TData, TValue>) {
    const [sorting, setSorting] = useState<SortingState>([])
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        state: {
            sorting,
            columnFilters,
            globalFilter: searchQuery,
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onGlobalFilterChange: onSearchQueryChange,
        globalFilterFn: 'includesString',
    })

    // Update credit type filter
    const handleCreditTypeChange = (value: string) => {
        const newValue = value === 'all' ? undefined : value;
        onCreditTypeChange(newValue);
    }

    const hasNextPage = currentPage * pageSize < totalCount;

    return (
        <div>
            <div className="flex items-center gap-4 py-4">
                <div className="flex-1">
                    <label className="text-sm font-medium mb-1 block">Search Description</label>
                    <Input
                        placeholder="Search by description"
                        value={searchQuery}
                        onChange={(event) => onSearchQueryChange(event.target.value)}
                        className="max-w-sm"
                    />
                </div>
                {loadingSpinner &&
                    <div>
                        {loadingSpinner}
                    </div>
                }

                <div>
                    <label className="text-sm font-medium mb-1 block">Credit Type</label>
                    <div className="flex items-center gap-2">
                        <Select
                            value={credit_type_id ?? 'all'}
                            onValueChange={handleCreditTypeChange}
                        >
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Select type"/>
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Types</SelectItem>
                                {creditTypes.map((type) => (
                                    <SelectItem key={type.id} value={type.id}>
                                        {type.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <div>
                    <label className="text-sm font-medium mb-1 block">Time Period</label>
                    <Select value={timePeriod} onValueChange={onTimePeriodChange}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Select period"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Time</SelectItem>
                            <SelectItem value="24h">Last 24 Hours</SelectItem>
                            <SelectItem value="7d">Last 7 Days</SelectItem>
                            <SelectItem value="30d">Last 30 Days</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    No results.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
                <div className="flex items-center justify-end space-x-2 py-4">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPageChange(currentPage + 1)}
                        disabled={!hasNextPage}
                    >
                        Next
                    </Button>
                </div>
            </div>
        </div>
    )
}
