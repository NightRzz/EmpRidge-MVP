import { Alert, Box, Card, CardContent, CardMedia, CircularProgress, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { getRecipeById } from '../services/recipesApi'

export default function RecipeDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const recipeId = Number(id)

  const recipeQuery = useQuery({
    queryKey: ['recipe', recipeId],
    queryFn: () => getRecipeById(recipeId),
    enabled: Number.isInteger(recipeId) && recipeId > 0,
  })

  if (!Number.isInteger(recipeId) || recipeId <= 0) {
    return <Alert severity="warning">Nieprawidłowe ID przepisu.</Alert>
  }

  if (recipeQuery.isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (recipeQuery.isError || !recipeQuery.data) {
    return <Alert severity="error">Nie udało się pobrać szczegółów przepisu.</Alert>
  }

  const recipe = recipeQuery.data
  return (
    <Card sx={{ bgcolor: 'background.paper' }}>
      {recipe.image_url  && <CardMedia component="img" height="600"  image={recipe.image_url + "/large"} alt={recipe.title} />}
      <CardContent>
        <Typography variant="h4" component="h1" gutterBottom sx={{ color: 'text.primary' }}>
          {recipe.title}
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
          {recipe.instructions || 'Brak instrukcji.'}
        </Typography>
      </CardContent>
    </Card>
  )
}
