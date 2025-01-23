import { useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  currentPage?: number;
  pageSize?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
  searchQuery?: string;
  onSearchQueryChange?: (value: string) => void;
  loadingSpinner?: React.ReactNode;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  currentPage,
  pageSize,
  totalCount,
  onPageChange,
  loadingSpinner,
  searchQuery,
  onSearchQueryChange,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const showPagination = currentPage !== undefined && 
    pageSize !== undefined && 
    totalCount !== undefined && 
    onPageChange !== undefined;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        {onSearchQueryChange && (
          <div className="flex items-center gap-2">
            <Input
              placeholder="Search..."
              value={searchQuery ?? ""}
              onChange={(event) => onSearchQueryChange(event.target.value)}
              className="max-w-sm"
            />
          </div>
        )}
        {loadingSpinner}
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
                  );
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
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {showPagination && (
        <div className="flex items-center justify-end space-x-2">
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
            disabled={currentPage * pageSize >= totalCount}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
} 