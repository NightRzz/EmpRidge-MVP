import { Box, Pagination, TablePagination } from '@mui/material'

export type ListPaginationProps = {
  total: number
  page: number
  rowsPerPage: number
  onPageChange: (nextPage: number) => void
  onRowsPerPageChange?: (nextRowsPerPage: number) => void
  rowsPerPageOptions?: number[]
}

/** Paginacja w UI; `total` to liczba wszystkich elementów już pobranych po stronie klienta. */
export default function ListPagination({
  total,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  rowsPerPageOptions = [10, 15, 25, 50],
}: ListPaginationProps) {
  if (total <= 0) return null

  const numberedOnly = typeof onRowsPerPageChange !== 'function'
  const pageCount = Math.ceil(total / rowsPerPage) || 1

  if (numberedOnly) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Pagination
          color="primary"
          count={pageCount}
          page={page + 1}
          onChange={(_, nextOneBased) => onPageChange(nextOneBased - 1)}
        />
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
      <TablePagination
        component="div"
        count={total}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={rowsPerPageOptions}
        onPageChange={(_, next) => onPageChange(next)}
        onRowsPerPageChange={(e) =>
          onRowsPerPageChange(Number.parseInt(e.target.value, 10))
        }
        labelRowsPerPage="Na stronę:"
        labelDisplayedRows={({ from, to, count }) =>
          `${from}–${to} z ${count !== -1 ? count : `${to}+`}`
        }
      />
    </Box>
  )
}
