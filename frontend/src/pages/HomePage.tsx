import { Alert, Box, CircularProgress, Grid, Stack, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import IngredientAutocomplete from '../components/IngredientAutocomplete'
import ListPagination from '../components/ListPagination'
import RecipeCard from '../components/RecipeCard'
import SearchFilters from '../components/SearchFilters'
import { fetchAllRecipes } from '../services/recipesApi'
import { searchRecipes, type SearchRecipeItem } from '../services/searchApi'
import type { Ingredient } from '../types/ingredient'

const ROWS_PER_PAGE = 24

export default function HomePage() {
  const [selectedIngredients, setSelectedIngredients] = useState<Ingredient[]>([])
  const [categoryId, setCategoryId] = useState<number | null>(null)
  const [areaId, setAreaId] = useState<number | null>(null)
  const [minRatio, setMinRatio] = useState(0)
  const [maxIngredients, setMaxIngredients] = useState<number | null>(null)

  const [page, setPage] = useState(0)

  const ingredientIds = selectedIngredients.map((i) => i.id)
  const ingredientIdsKey = ingredientIds.join('|')
  const isSearchMode = ingredientIds.length > 0

  const searchQuery = useQuery({
    queryKey: [
      'search-recipes',
      ingredientIdsKey,
      categoryId,
      areaId,
      minRatio,
      maxIngredients,
    ],
    queryFn: () =>
      searchRecipes({
        ingredient_ids: ingredientIds,
        category_id: categoryId ?? undefined,
        area_id: areaId ?? undefined,
        min_matching_ratio: minRatio,
        max_total_ingredients: maxIngredients ?? undefined,
      }),
    enabled: isSearchMode,
  })

  const browseQuery = useQuery({
    queryKey: ['recipes', 'full'],
    queryFn: async () => fetchAllRecipes(),
    enabled: !isSearchMode,
    staleTime: 60_000,
  })

  const activeQuery = isSearchMode ? searchQuery : browseQuery
  const isLoading = activeQuery.isLoading
  const isError = activeQuery.isError

  const searchAll = useMemo(
    () => (searchQuery.data ?? []) as SearchRecipeItem[],
    [searchQuery.data],
  )
  const browseAll = useMemo(() => browseQuery.data ?? [], [browseQuery.data])

  const totalCount = isSearchMode ? searchAll.length : browseAll.length
  const pageCount = Math.ceil(totalCount / ROWS_PER_PAGE)
  const currentPage = pageCount === 0 ? 0 : Math.min(page, pageCount - 1)

  const browseVisible = useMemo(
    () =>
      browseAll.slice(
        currentPage * ROWS_PER_PAGE,
        currentPage * ROWS_PER_PAGE + ROWS_PER_PAGE,
      ),
    [browseAll, currentPage],
  )

  const searchVisible = useMemo(
    () =>
      searchAll.slice(
        currentPage * ROWS_PER_PAGE,
        currentPage * ROWS_PER_PAGE + ROWS_PER_PAGE,
      ),
    [searchAll, currentPage],
  )

  const resetFilters = () => {
    setCategoryId(null)
    setAreaId(null)
    setMinRatio(0)
    setMaxIngredients(null)
    setPage(0)
  }

  const handleIngredientsChange = (next: Ingredient[]) => {
    setSelectedIngredients(next)
    setPage(0)
  }

  const handleCategoryChange = (next: number | null) => {
    setCategoryId(next)
    setPage(0)
  }

  const handleAreaChange = (next: number | null) => {
    setAreaId(next)
    setPage(0)
  }

  const handleMinRatioChange = (next: number) => {
    setMinRatio(next)
    setPage(0)
  }

  const handleMaxIngredientsChange = (next: number | null) => {
    setMaxIngredients(next)
    setPage(0)
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h4" component="h1" sx={{ color: 'text.primary'}}>
        Wyszukaj przepisy
      </Typography>

      <IngredientAutocomplete
        selected={selectedIngredients}
        onChange={handleIngredientsChange}
      />

      <SearchFilters
        categoryId={categoryId}
        areaId={areaId}
        minRatio={minRatio}
        maxIngredients={maxIngredients}
        onCategoryChange={handleCategoryChange}
        onAreaChange={handleAreaChange}
        onMinRatioChange={handleMinRatioChange}
        onMaxIngredientsChange={handleMaxIngredientsChange}
        onReset={resetFilters}
        disabled={!isSearchMode}
      />

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="error">Nie udało się pobrać przepisów. Spróbuj ponownie.</Alert>
      )}

      {!isLoading && !isError && isSearchMode && totalCount === 0 && (
        <Alert severity="info">
          Brak przepisów pasujących do wybranych składników i filtrów.
        </Alert>
      )}

      {!isLoading && !isError && !isSearchMode && totalCount === 0 && (
        <Alert severity="info">Brak przepisów do wyświetlenia.</Alert>
      )}

      {!isLoading &&
        !isError &&
        isSearchMode &&
        totalCount > 0 && (
        <>
          <Typography variant="body2" color="text.secondary">
            Znaleziono {totalCount} przepisów
          </Typography>
          <Grid container spacing={2}>
            {searchVisible.map((r) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={r.id}>
                <RecipeCard
                  id={r.id}
                  title={r.title}
                  imageUrl={r.image_url}
                  matchedCount={r.matched_count}
                  totalCount={r.total_count}
                  matchingRatio={r.matching_ratio}
                />
              </Grid>
            ))}
          </Grid>
          <ListPagination
            total={totalCount}
            page={currentPage}
            rowsPerPage={ROWS_PER_PAGE}
            onPageChange={setPage}
          />
        </>
      )}

      {!isLoading && !isError && !isSearchMode && totalCount > 0 && (
        <>
          <Typography variant="body2" color="text.secondary">
            Łącznie {totalCount} przepisów
          </Typography>
          <Grid container spacing={2}>
            {browseVisible.map((r) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={r.id}>
                <RecipeCard id={r.id} title={r.title} imageUrl={r.image_url} />
              </Grid>
            ))}
          </Grid>
          <ListPagination
            total={totalCount}
            page={currentPage}
            rowsPerPage={ROWS_PER_PAGE}
            onPageChange={setPage}
          />
        </>
      )}
    </Stack>
  )
}
