import { Button } from "@/components/ui/button"

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  SortingState,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnFiltersState,
  FilterFn,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { CreditType } from "@/types/creditType"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  creditTypes: CreditType[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
  creditTypes,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [description, setDescription] = useState('')
  const [timePeriod, setTimePeriod] = useState('')

  // Custom filter function for time period
  const timeFilterFn: FilterFn<any> = (row, columnId, value) => {
    if (value === 'all') return true
    
    const transactionDate = new Date(row.getValue('created_at'))
    const today = new Date()
    
    switch (value) {
      case 'today':
        return transactionDate.toDateString() === today.toDateString()
      case 'week':
        const weekAgo = new Date(today.setDate(today.getDate() - 7))
        return transactionDate >= weekAgo
      case 'month':
        return (
          transactionDate.getMonth() === today.getMonth() &&
          transactionDate.getFullYear() === today.getFullYear()
        )
      case 'year':
        return transactionDate.getFullYear() === today.getFullYear()
      default:
        return true
    }
  }

  // Add this custom filter function for credit type
  // const creditTypeFilterFn: FilterFn<any> = (row, columnId, filterValue) => {
  //   // Add this console.log to debug
  //   console.log('Filtering:', {
  //     rowValue: row.getValue(columnId),
  //     filterValue,
  //     columnId
  //   })
    
  //   if (!filterValue || filterValue === 'all') return true
  //   return row.getValue(columnId) === filterValue
  // }

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      globalFilter: description,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setDescription,
    globalFilterFn: 'includesString',
    filterFns: {
      timePeriod: timeFilterFn,
      // creditType: creditTypeFilterFn, // Add the custom filter function
    },
  })

  // Update credit type filter with debugging
  const handleCreditTypeChange = (value: string) => {
    console.log('Credit type changed to:', value)
    table.getColumn('credit_type')?.setFilterValue(value)
  }

  // Update time period filter
  useEffect(() => {
    table.getColumn('created_at')?.setFilterValue(timePeriod)
  }, [timePeriod])

  // Add this useEffect to monitor filter changes
  useEffect(() => {
    console.log('Current filters:', table.getState().columnFilters)
  }, [columnFilters])

  return (
    <div>
      <div className="flex items-center gap-4 py-4">
        <div className="flex-1">
          <label className="text-sm font-medium mb-1 block">Search Description</label>
          <Input
            placeholder="Search by description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="max-w-sm"
          />
        </div>
        
        <div>
          <label className="text-sm font-medium mb-1 block">Credit Type</label>
          <Select 
            value={table.getColumn('credit_type')?.getFilterValue() as string ?? 'all'} 
            onValueChange={handleCreditTypeChange}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select type" />
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

        <div>
          <label className="text-sm font-medium mb-1 block">Time Period</label>
          <Select value={timePeriod} onValueChange={setTimePeriod}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="year">This Year</SelectItem>
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
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
