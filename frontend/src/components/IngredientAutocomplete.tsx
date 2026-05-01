import { Autocomplete, TextField } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { suggestIngredients } from '../services/ingredientsApi'
import type { Ingredient } from '../types/ingredient'
import { useDebounce } from '../hooks/useDebounce'

type Props = {
  selected: Ingredient[]
  onChange: (ingredients: Ingredient[]) => void
}

export default function IngredientAutocomplete({ selected, onChange }: Props) {
  const [inputValue, setInputValue] = useState('')
  const debouncedQuery = useDebounce(inputValue, 300)

  const suggestionsQuery = useQuery({
    queryKey: ['ingredient-suggestions', debouncedQuery],
    queryFn: () => suggestIngredients(debouncedQuery, 15),
    enabled: debouncedQuery.length >= 2,
  })

  const options = suggestionsQuery.data ?? []

  return (
    <Autocomplete
      multiple
      options={options}
      value={selected}
      onChange={(_, value) => onChange(value)}
      getOptionLabel={(option) => option.name}
      isOptionEqualToValue={(option, value) => option.id === value.id}
      filterOptions={(x) => x}
      inputValue={inputValue}
      onInputChange={(_, value) => setInputValue(value)}
      loading={suggestionsQuery.isFetching}
      noOptionsText={debouncedQuery.length < 2 ? 'Wpisz min. 2 znaki' : 'Brak wyników'}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Wyszukaj składniki"
          placeholder="np. chicken, rice..."
        />
      )}
    />
  )
}
