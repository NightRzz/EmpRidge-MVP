import { Alert, Box, Card, CardContent, CardMedia, CircularProgress, Grid, Stack, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { Link as RouterLink } from 'react-router-dom'

import { listRecipes } from '../services/recipesApi'

const DEFAULT_IMAGE =
  'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'

export default function HomePage() {
  const recipesQuery = useQuery({
    queryKey: ['recipes', { skip: 0, limit: 24 }],
    queryFn: () => listRecipes(0, 24),
  })

  if (recipesQuery.isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (recipesQuery.isError) {
    return <Alert severity="error">Nie udało się pobrać listy przepisów.</Alert>
  }

  const recipes = recipesQuery.data ?? []
  if (recipes.length === 0) {
    return <Alert severity="info">Brak przepisów do wyświetlenia.</Alert>
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h4" component="h1">
        Recipe Gallery
      </Typography>

      <Grid container spacing={2}>
        {recipes.map((recipe) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={recipe.id}>
            <Card
              component={RouterLink}
              to={`/recipe/${recipe.id}`}
              sx={{
                textDecoration: 'none',
                height: '100%',
                color: 'text.primary',
                '& .MuiTypography-root': { color: 'text.primary' },
              }}
            >
              <CardMedia
                component="img"
                height="70%"
                width="10%"
                image={recipe.image_url || DEFAULT_IMAGE}
                alt={recipe.title}
              />
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ color: 'text.primary' }}>
                  {recipe.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  )
}
