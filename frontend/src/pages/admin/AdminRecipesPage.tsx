import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
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
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlaylistAdd as PlaylistAddIcon,
} from '@mui/icons-material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useRef, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import {
  createRecipe,
  deleteRecipe,
  fetchAllRecipes,
  getRecipeById,
  replaceRecipeIngredients,
  updateRecipe,
  type RecipeIngredientAssignment,
  type RecipePayload,
} from '../../services/recipesApi'
import { suggestIngredients } from '../../services/ingredientsApi'
import { listCategories, type Category } from '../../services/categoriesApi'
import { listAreas, type Area } from '../../services/areasApi'
import type { Recipe } from '../../types/recipe'
import type { Ingredient } from '../../types/ingredient'
import ConfirmDialog from '../../components/ConfirmDialog'
import ListPagination from '../../components/ListPagination'
import { useDebounce } from '../../hooks/useDebounce'

const recipeSchema = z.object({
  title: z.string().min(1, 'Tytuł jest wymagany'),
  instructions: z.string(),
  image_url: z.string(),
  youtube_url: z.string(),
  category_id: z.number().nullable(),
  area_id: z.number().nullable(),
})

type RecipeFormData = z.infer<typeof recipeSchema>

type SnackState = { open: boolean; message: string; severity: 'success' | 'error' }

type IngredientLineRow = {
  rowKey: string
  ingredient: Ingredient | null
  measure: string
}

export default function AdminRecipesPage() {
  const queryClient = useQueryClient()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Recipe | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Recipe | null>(null)
  const [snack, setSnack] = useState<SnackState>({ open: false, message: '', severity: 'success' })

  const [savingRecipe, setSavingRecipe] = useState(false)

  const [recipePage, setRecipePage] = useState(0)
  const [recipeRowsPerPage, setRecipeRowsPerPage] = useState(15)

  const recipesQuery = useQuery({
    queryKey: ['admin-recipes-full'],
    queryFn: () => fetchAllRecipes(),
    staleTime: 30_000,
  })

  const allRecipes = useMemo(() => recipesQuery.data ?? [], [recipesQuery.data])
  const recipePageCount = Math.ceil(allRecipes.length / recipeRowsPerPage)
  const currentRecipePage = recipePageCount === 0 ? 0 : Math.min(recipePage, recipePageCount - 1)

  const recipes = useMemo(
    () =>
      allRecipes.slice(
        currentRecipePage * recipeRowsPerPage,
        currentRecipePage * recipeRowsPerPage + recipeRowsPerPage,
      ),
    [allRecipes, currentRecipePage, recipeRowsPerPage],
  )

  const categoriesQuery = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: listCategories,
  })

  const areasQuery = useQuery<Area[]>({
    queryKey: ['areas'],
    queryFn: listAreas,
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteRecipe(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-recipes-full'] })
      setDeleteTarget(null)
      setSnack({ open: true, message: 'Przepis usunięty.', severity: 'success' })
    },
    onError: () => setSnack({ open: true, message: 'Nie udało się usunąć przepisu.', severity: 'error' }),
  })

  const handleSaveRecipeWithIngredients = async (
    formData: RecipeFormData,
    assignments: RecipeIngredientAssignment[],
  ) => {
    const payload: RecipePayload = {
      title: formData.title,
      instructions: formData.instructions || null,
      image_url: formData.image_url || null,
      youtube_url: formData.youtube_url || null,
      category_id: formData.category_id,
      area_id: formData.area_id,
    }
    setSavingRecipe(true)
    try {
      let targetId: number
      if (editing) {
        await updateRecipe(editing.id, payload)
        targetId = editing.id
      } else {
        const created = await createRecipe(payload)
        targetId = created.id
      }
      await replaceRecipeIngredients(targetId, assignments)
      queryClient.invalidateQueries({ queryKey: ['admin-recipes-full'] })
      queryClient.invalidateQueries({ queryKey: ['recipe', targetId] })
      setDialogOpen(false)
      setEditing(null)
      setSnack({ open: true, message: 'Przepis zapisany.', severity: 'success' })
    } catch {
      setSnack({ open: true, message: 'Nie udało się zapisać przepisu lub składników.', severity: 'error' })
    } finally {
      setSavingRecipe(false)
    }
  }

  const categories = categoriesQuery.data ?? []
  const areas = areasQuery.data ?? []

  const categoryMap = new Map(categories.map((c) => [c.id, c.name]))
  const areaMap = new Map(areas.map((a) => [a.id, a.name]))

  return (
    <Stack spacing={2}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Przepisy
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => { setEditing(null); setDialogOpen(true) }}
        >
          Dodaj
        </Button>
      </Box>

      {recipesQuery.isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {recipesQuery.isError && (
        <Alert severity="error">Nie udało się pobrać listy przepisów.</Alert>
      )}

      {!recipesQuery.isLoading && recipesQuery.data && recipes.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          Brak przepisów.
        </Typography>
      )}

      {recipes.length > 0 && (
        <>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Tytuł</TableCell>
                  <TableCell>Kategoria</TableCell>
                  <TableCell>Kraj</TableCell>
                  <TableCell align="right">Akcje</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recipes.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.id}</TableCell>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{item.category_id ? categoryMap.get(item.category_id) ?? '—' : '—'}</TableCell>
                    <TableCell>{item.area_id ? areaMap.get(item.area_id) ?? '—' : '—'}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => { setEditing(item); setDialogOpen(true) }}
                        aria-label="edytuj"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => setDeleteTarget(item)}
                        aria-label="usuń"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <ListPagination
            total={allRecipes.length}
            page={currentRecipePage}
            rowsPerPage={recipeRowsPerPage}
            rowsPerPageOptions={[10, 15, 25, 50]}
            onPageChange={setRecipePage}
            onRowsPerPageChange={(n) => {
              setRecipeRowsPerPage(n)
              setRecipePage(0)
            }}
          />
        </>
      )}

      <RecipeFormDialog
        key={`${editing?.id ?? 'new'}-${dialogOpen ? 'open' : 'closed'}`}
        open={dialogOpen}
        onClose={() => { setDialogOpen(false); setEditing(null) }}
        recipeSummary={editing}
        categories={categories}
        areas={areas}
        onSave={handleSaveRecipeWithIngredients}
        loading={savingRecipe}
      />

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Usuń przepis"
        message={`Czy na pewno chcesz usunąć przepis „${deleteTarget?.title}"?`}
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

function IngredientAssignRow({
  line,
  excludeIngredientIds,
  onIngredientChange,
  onMeasureChange,
  onRemove,
  disabled,
}: {
  line: IngredientLineRow
  excludeIngredientIds: number[]
  onIngredientChange: (ingredient: Ingredient | null) => void
  onMeasureChange: (m: string) => void
  onRemove: () => void
  disabled?: boolean
}) {
  const [inputValue, setInputValue] = useState('')
  const debouncedQuery = useDebounce(inputValue, 300)

  const suggestionsQuery = useQuery({
    queryKey: ['ingredient-assign-suggestions', debouncedQuery, excludeIngredientIds],
    queryFn: () => suggestIngredients(debouncedQuery, 15),
    enabled: debouncedQuery.length >= 2,
  })

  const options = useMemo(() => {
    const list = suggestionsQuery.data ?? []
    return list.filter(
      (item) =>
        item.id === line.ingredient?.id || !excludeIngredientIds.includes(item.id),
    )
  }, [excludeIngredientIds, line.ingredient?.id, suggestionsQuery.data])

  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mb: 1.5 }}>
      <Autocomplete
        sx={{ flex: 2, minWidth: 0 }}
        value={line.ingredient}
        onChange={(_, value) => onIngredientChange(value)}
        options={options}
        loading={suggestionsQuery.isFetching}
        getOptionLabel={(o) => o.name}
        isOptionEqualToValue={(opt, val) => opt.id === val.id}
        inputValue={inputValue}
        onInputChange={(_, value) => setInputValue(value)}
        disabled={disabled}
        filterOptions={(x) => x}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Składnik z katalogu"
            placeholder="min. 2 znaki..."
          />
        )}
      />
      <TextField
        sx={{ flex: 1 }}
        label="Miara"
        value={line.measure}
        onChange={(e) => onMeasureChange(e.target.value)}
        disabled={disabled}
        placeholder="np. 1 szklanka"
      />
      <IconButton
        sx={{ mt: { sm: '4px' } }}
        onClick={onRemove}
        disabled={disabled}
        aria-label="usuń składnik"
      >
        <DeleteIcon />
      </IconButton>
    </Stack>
  )
}

function RecipeFormDialog({
  open,
  onClose,
  recipeSummary,
  categories,
  areas,
  onSave,
  loading,
}: {
  open: boolean
  onClose: () => void
  recipeSummary: Recipe | null
  categories: Category[]
  areas: Area[]
  onSave: (data: RecipeFormData, assignments: RecipeIngredientAssignment[]) => void | Promise<void>
  loading: boolean
}) {
  const newRowKeyRef = useRef(0)

  const detailQuery = useQuery({
    queryKey: ['recipe', recipeSummary?.id ?? 0],
    queryFn: () => getRecipeById(recipeSummary!.id),
    enabled: Boolean(open && recipeSummary?.id),
  })

  const formSource = recipeSummary ?? null

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<RecipeFormData>({
    resolver: zodResolver(recipeSchema),
    values: formSource
      ? {
          title: formSource.title,
          instructions: formSource.instructions ?? '',
          image_url: formSource.image_url ?? '',
          youtube_url: formSource.youtube_url ?? '',
          category_id: formSource.category_id,
          area_id: formSource.area_id,
        }
      : {
          title: '',
          instructions: '',
          image_url: '',
          youtube_url: '',
          category_id: null,
          area_id: null,
        },
  })

  const baseIngredientLines = useMemo(() => {
    if (!recipeSummary) return []
    const d = detailQuery.data
    if (!d || d.id !== recipeSummary.id) return []
    const lines = d.ingredients ?? []
    return lines.map((li, idx) => ({
      rowKey: `ing-${li.ingredient_id}-${idx}`,
      ingredient: {
        id: li.ingredient_id,
        name: li.name,
        image_url: li.image_url ?? '',
      },
      measure: li.measure ?? '',
    }))
  }, [recipeSummary, detailQuery.data])
  const [ingredientLinesOverride, setIngredientLinesOverride] = useState<IngredientLineRow[] | null>(null)
  const ingredientLines = ingredientLinesOverride ?? baseIngredientLines

  const excludedForRow = useMemo(
    () =>
      ingredientLines
        .map((l) => l.ingredient?.id)
        .filter((id): id is number => typeof id === 'number'),
    [ingredientLines],
  )

  const appendRow = () => {
    newRowKeyRef.current += 1
    setIngredientLinesOverride((prev) => [
      ...(prev ?? baseIngredientLines),
      { rowKey: `new-${newRowKeyRef.current}`, ingredient: null, measure: '' },
    ])
  }

  const removeRowAt = (rowKey: string) => {
    setIngredientLinesOverride((prev) =>
      (prev ?? baseIngredientLines).filter((r) => r.rowKey !== rowKey),
    )
  }

  const onSubmitInner = async (data: RecipeFormData) => {
    const orphanedMeasure = ingredientLines.some(
      (line) => !line.ingredient && line.measure.trim() !== '',
    )
    if (orphanedMeasure) return

    const assignments: RecipeIngredientAssignment[] = ingredientLines
      .filter((line): line is IngredientLineRow & { ingredient: Ingredient } => line.ingredient !== null)
      .map((line) => ({
        ingredient_id: line.ingredient.id,
        measure: line.measure.trim() ? line.measure.trim() : null,
      }))

    await onSave(data, assignments)
  }

  const awaitingDetail = Boolean(open && recipeSummary?.id && detailQuery.isPending)
  const ingredientEditorReady =
    open &&
    (!recipeSummary ||
      (detailQuery.isSuccess &&
        !!detailQuery.data &&
        detailQuery.data.id === recipeSummary.id))

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth scroll="paper">
      <form
        onSubmit={(e) => {
          void handleSubmit(onSubmitInner)(e)
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', color: 'text.primary' }}>{recipeSummary ? 'Edytuj przepis' : 'Nowy przepis'}</DialogTitle>
        <DialogContent sx={{ pb: 1 }}>
          <TextField
            {...register('title')}
            label="Tytuł"
            fullWidth
            margin="normal"
            error={!!errors.title}
            helperText={errors.title?.message}
            autoFocus
          />
          <TextField
            {...register('instructions')}
            label="Instrukcje"
            fullWidth
            margin="normal"
            multiline
            minRows={3}
          />
          <TextField
            {...register('image_url')}
            label="URL zdjęcia"
            fullWidth
            margin="normal"
          />
          <TextField
            {...register('youtube_url')}
            label="URL YouTube"
            fullWidth
            margin="normal"
          />

          <Controller
            name="category_id"
            control={control}
            render={({ field }) => (
              <TextField
                select
                label="Kategoria"
                fullWidth
                margin="normal"
                value={field.value ?? ''}
                onChange={(e) =>
                  field.onChange(e.target.value === '' ? null : Number(e.target.value))
                }
              >
                <MenuItem value="">Brak</MenuItem>
                {categories.map((c) => (
                  <MenuItem key={c.id} value={c.id}>
                    {c.name}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />

          <Controller
            name="area_id"
            control={control}
            render={({ field }) => (
              <TextField
                select
                label="Kraj"
                fullWidth
                margin="normal"
                value={field.value ?? ''}
                onChange={(e) =>
                  field.onChange(e.target.value === '' ? null : Number(e.target.value))
                }
              >
                <MenuItem value="">Brak</MenuItem>
                {areas.map((a) => (
                  <MenuItem key={a.id} value={a.id}>
                    {a.name}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />

          <Typography variant="subtitle1" sx={{ mt: 2, mb: 0.5 }}>
            Składniki
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Wybieraj tylko składniki z katalogu; nowych pozycji nie dodaje się tutaj (panel „Składniki”).
          </Typography>

          {awaitingDetail && (
            <Box sx={{ py: 2 }}>
              <CircularProgress size={24} />
              <Typography component="span" variant="body2" sx={{ ml: 2 }}>
                Wczytywanie listy składników...
              </Typography>
            </Box>
          )}

          {ingredientEditorReady && (
            <>
              {ingredientLines.map((line, index) => {
                const excluded = excludedForRow.filter(
                  (id) => line.ingredient?.id !== id,
                )
                return (
                  <IngredientAssignRow
                    key={line.rowKey}
                    line={line}
                    excludeIngredientIds={excluded}
                    disabled={loading}
                    onIngredientChange={(ingredient) =>
                      setIngredientLinesOverride((prev) =>
                        (prev ?? baseIngredientLines).map((r, i) =>
                          i === index ? { ...r, ingredient } : r,
                        ),
                      )
                    }
                    onMeasureChange={(measure) =>
                      setIngredientLinesOverride((prev) =>
                        (prev ?? baseIngredientLines).map((r, i) =>
                          i === index ? { ...r, measure } : r,
                        ),
                      )
                    }
                    onRemove={() => removeRowAt(line.rowKey)}
                  />
                )
              })}
              <Button
                type="button"
                startIcon={<PlaylistAddIcon />}
                onClick={appendRow}
                disabled={loading}
                sx={{ mt: 1 }}
              >
                Dodaj linię składnika
              </Button>
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={onClose} disabled={loading}>
            Anuluj
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || awaitingDetail}
          >
            {loading ? 'Zapisywanie...' : recipeSummary ? 'Zapisz' : 'Utwórz'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}
