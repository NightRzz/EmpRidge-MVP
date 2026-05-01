import { Button, Grid, MenuItem, Slider, TextField, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'

import { listCategories, type Category } from '../services/categoriesApi'
import { listAreas, type Area } from '../services/areasApi'

type SearchFiltersProps = {
  categoryId: number | null
  areaId: number | null
  minRatio: number
  maxIngredients: number | null
  onCategoryChange: (id: number | null) => void
  onAreaChange: (id: number | null) => void
  onMinRatioChange: (value: number) => void
  onMaxIngredientsChange: (value: number | null) => void
  onReset: () => void
  disabled?: boolean
}

export default function SearchFilters({
  categoryId,
  areaId,
  minRatio,
  maxIngredients,
  onCategoryChange,
  onAreaChange,
  onMinRatioChange,
  onMaxIngredientsChange,
  onReset,
  disabled = false,
}: SearchFiltersProps) {
  const categoriesQuery = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: listCategories,
  })
  const areasQuery = useQuery<Area[]>({
    queryKey: ['areas'],
    queryFn: listAreas,
  })

  const categories = categoriesQuery.data ?? []
  const areas = areasQuery.data ?? []

  return (
    <Grid container spacing={2} sx={{ alignItems: 'center' }}>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <TextField
          select
          fullWidth
          size="small"
          label="Kategoria"
          value={categoryId ?? ''}
          onChange={(e) => onCategoryChange(e.target.value ? Number(e.target.value) : null)}
          disabled={disabled}
        >
          <MenuItem value="">Wszystkie</MenuItem>
          {categories.map((c) => (
            <MenuItem key={c.id} value={c.id}>
              {c.name}
            </MenuItem>
          ))}
        </TextField>
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <TextField
          select
          fullWidth
          size="small"
          label="Kraj"
          value={areaId ?? ''}
          onChange={(e) => onAreaChange(e.target.value ? Number(e.target.value) : null)}
          disabled={disabled}
        >
          <MenuItem value="">Wszystkie</MenuItem>
          {areas.map((a) => (
            <MenuItem key={a.id} value={a.id}>
              {a.name}
            </MenuItem>
          ))}
        </TextField>
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 2 }}>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          Min. dopasowanie: {minRatio}%
        </Typography>
        <Slider
          value={minRatio}
          onChange={(_, v) => onMinRatioChange(v as number)}
          min={0}
          max={100}
          step={5}
          size="small"
          disabled={disabled}
          valueLabelDisplay="auto"
        />
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 2 }}>
        <TextField
          fullWidth
          size="small"
          type="number"
          label="Maks. składników"
          value={maxIngredients ?? ''}
          onChange={(e) =>
            onMaxIngredientsChange(e.target.value ? Number(e.target.value) : null)
          }
          disabled={disabled}
          slotProps={{ htmlInput: { min: 1, max: 50 } }}
        />
      </Grid>

      <Grid size={{ xs: 12, md: 2 }}>
        <Button fullWidth variant="outlined" size="small" onClick={onReset} disabled={disabled}>
          Reset filtrów
        </Button>
      </Grid>
    </Grid>
  )
}
