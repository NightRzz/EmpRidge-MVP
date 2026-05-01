import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Snackbar,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Paper,
} from '@mui/material'
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import {
  createIngredient,
  deleteIngredient,
  fetchAllIngredients,
  updateIngredient,
} from '../../services/ingredientsApi'
import type { Ingredient } from '../../types/ingredient'
import ConfirmDialog from '../../components/ConfirmDialog'
import ListPagination from '../../components/ListPagination'

const ingredientSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  image_url: z.string().min(1, 'URL obrazka jest wymagany'),
})

type IngredientFormData = z.infer<typeof ingredientSchema>

type SnackState = { open: boolean; message: string; severity: 'success' | 'error' }

export default function AdminIngredientsPage() {
  const queryClient = useQueryClient()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Ingredient | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Ingredient | null>(null)
  const [snack, setSnack] = useState<SnackState>({ open: false, message: '', severity: 'success' })

  const [ingredientPage, setIngredientPage] = useState(0)
  const [ingredientRowsPerPage, setIngredientRowsPerPage] = useState(15)

  const ingredientsQuery = useQuery({
    queryKey: ['admin-ingredients-full'],
    queryFn: () => fetchAllIngredients(),
    staleTime: 30_000,
  })

  const allIngredients = useMemo(() => ingredientsQuery.data ?? [], [ingredientsQuery.data])
  const ingredientPageCount = Math.ceil(allIngredients.length / ingredientRowsPerPage)
  const currentIngredientPage =
    ingredientPageCount === 0 ? 0 : Math.min(ingredientPage, ingredientPageCount - 1)

  const ingredients = useMemo(
    () =>
      allIngredients.slice(
        currentIngredientPage * ingredientRowsPerPage,
        currentIngredientPage * ingredientRowsPerPage + ingredientRowsPerPage,
      ),
    [allIngredients, currentIngredientPage, ingredientRowsPerPage],
  )

  const createMut = useMutation({
    mutationFn: (data: IngredientFormData) => createIngredient(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-ingredients-full'] })
      setDialogOpen(false)
      setSnack({ open: true, message: 'Składnik utworzony.', severity: 'success' })
    },
    onError: () => setSnack({ open: true, message: 'Nie udało się utworzyć składnika.', severity: 'error' }),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<IngredientFormData> }) =>
      updateIngredient(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-ingredients-full'] })
      setDialogOpen(false)
      setEditing(null)
      setSnack({ open: true, message: 'Składnik zaktualizowany.', severity: 'success' })
    },
    onError: () => setSnack({ open: true, message: 'Nie udało się zaktualizować składnika.', severity: 'error' }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteIngredient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-ingredients-full'] })
      setDeleteTarget(null)
      setSnack({ open: true, message: 'Składnik usunięty.', severity: 'success' })
    },
    onError: () => setSnack({ open: true, message: 'Nie udało się usunąć składnika.', severity: 'error' }),
  })

  const isMutating = createMut.isPending || updateMut.isPending

  const handleOpenCreate = () => {
    setEditing(null)
    setDialogOpen(true)
  }

  const handleOpenEdit = (item: Ingredient) => {
    setEditing(item)
    setDialogOpen(true)
  }

  const handleFormSubmit = (data: IngredientFormData) => {
    if (editing) {
      updateMut.mutate({ id: editing.id, data })
    } else {
      createMut.mutate(data)
    }
  }

  return (
    <Stack spacing={2}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Składniki
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}>
          Dodaj
        </Button>
      </Box>

      {ingredientsQuery.isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {ingredientsQuery.isError && (
        <Alert severity="error">Nie udało się pobrać listy składników.</Alert>
      )}

      {!ingredientsQuery.isLoading && ingredientsQuery.data && ingredients.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          Brak składników.
        </Typography>
      )}

      {ingredients.length > 0 && (
        <>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Nazwa</TableCell>
                  <TableCell>Obrazek</TableCell>
                  <TableCell align="right">Akcje</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ingredients.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.id}</TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.image_url}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleOpenEdit(item)} aria-label="edytuj">
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" onClick={() => setDeleteTarget(item)} aria-label="usuń">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <ListPagination
            total={allIngredients.length}
            page={currentIngredientPage}
            rowsPerPage={ingredientRowsPerPage}
            rowsPerPageOptions={[10, 15, 25, 50, 100]}
            onPageChange={setIngredientPage}
            onRowsPerPageChange={(n) => {
              setIngredientRowsPerPage(n)
              setIngredientPage(0)
            }}
          />
        </>
      )}

      <IngredientFormDialog
        open={dialogOpen}
        onClose={() => { setDialogOpen(false); setEditing(null) }}
        ingredient={editing}
        onSubmit={handleFormSubmit}
        loading={isMutating}
      />

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Usuń składnik"
        message={`Czy na pewno chcesz usunąć składnik „${deleteTarget?.name}"?`}
        onConfirm={() => deleteTarget && deleteMut.mutate(deleteTarget.id)}
        onCancel={() => setDeleteTarget(null)}
        loading={deleteMut.isPending}
      />

      <Snackbar
        open={snack.open}
        autoHideDuration={4000}
        onClose={() => setSnack((s) => ({ ...s, open: false }))}
      >
        <Alert severity={snack.severity} variant="filled" onClose={() => setSnack((s) => ({ ...s, open: false }))}>
          {snack.message}
        </Alert>
      </Snackbar>
    </Stack>
  )
}

function IngredientFormDialog({
  open,
  onClose,
  ingredient,
  onSubmit,
  loading,
}: {
  open: boolean
  onClose: () => void
  ingredient: Ingredient | null
  onSubmit: (data: IngredientFormData) => void
  loading: boolean
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<IngredientFormData>({
    resolver: zodResolver(ingredientSchema),
    values: ingredient
      ? { name: ingredient.name, image_url: ingredient.image_url }
      : { name: '', image_url: '' },
  })

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle sx={{ textAlign: 'center', color: 'text.primary' }}>{ingredient ? 'Edytuj składnik' : 'Nowy składnik'}</DialogTitle>
        <DialogContent>
          <TextField
            {...register('name')}
            label="Nazwa"
            fullWidth
            margin="normal"
            error={!!errors.name}
            helperText={errors.name?.message}
            autoFocus
          />
          <TextField
            {...register('image_url')}
            label="URL obrazka"
            fullWidth
            margin="normal"
            error={!!errors.image_url}
            helperText={errors.image_url?.message}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Anuluj
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Zapisywanie...' : ingredient ? 'Zapisz' : 'Utwórz'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}
