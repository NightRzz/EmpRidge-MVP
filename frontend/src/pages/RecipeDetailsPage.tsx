import {
  Alert,
  Avatar,
  Box,
  Card,
  CardContent,
  CardMedia,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  CircularProgress,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { getRecipeById } from '../services/recipesApi'
import { youtubeEmbedVideoId } from '../utils/youtubeEmbed'

const FALLBACK_INGREDIENT_IMG =
  'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=120&q=70'

function ingredientThumbUrl(url: string | null): string {
  const u = url?.trim()
  if (!u) return FALLBACK_INGREDIENT_IMG
  if (
    u.includes('themealdb.com/images/ingredients') &&
    /\.png$/i.test(u) &&
    !/-small\.png$/i.test(u)
  ) {
    return u.replace(/\.png$/i, '-Small.png')
  }
  return u
}

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
  const ingredientLines = recipe.ingredients ?? []
  const ytId = youtubeEmbedVideoId(recipe.youtube_url)
  const heroSrc = recipe.image_url


  return (
    <Card sx={{ bgcolor: 'background.paper', overflow: 'hidden' }}>
      {heroSrc && (
        <CardMedia
          component="img"

          image={heroSrc}
          alt={recipe.title}
          sx={{ objectFit: 'cover', maxHeight: '45vh', maxWidth: '30vw',py:3, width: '100%', margin: 'auto' }}
        />
      )}
      <CardContent sx={{ pb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ color: 'text.primary', fontWeight: 'bold' }}>
          {recipe.title}
        </Typography>

        {ytId && (
          <Box sx={{ my: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom sx={{ mb: 1.5, color: 'text.primary', fontWeight: 'bold' }}>
              Film
            </Typography>
            <Box
              sx={{
                width: '100%',
                maxWidth: 896,
                borderRadius: 1,
                overflow: 'hidden',
                aspectRatio: '16 / 9',
                margin: 'auto'
              }}
            >
              <iframe
                title={`YouTube — ${recipe.title}`}
                width="100%"
                height="100%"
                src={`https://www.youtube-nocookie.com/embed/${ytId}`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                loading="lazy"
                style={{ border: 0, display: 'block', margin: 'auto',  }}
              />
            </Box>
          </Box>
        )}

        <Typography variant="h6" component="h2" sx={{ mt: ytId ? 0 : 1, mb: 1.5, color: 'text.primary', fontWeight: 'bold' }}>
          Składniki
        </Typography>

        {ingredientLines.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Nie zapisano listy składników dla tego przepisu.
          </Typography>
        ) : (
          <List disablePadding sx={{ bgcolor: 'action.hover', borderRadius: 1, px: 1, py: 0.5 }}>
            {ingredientLines.map((line) => {
              const thumb = ingredientThumbUrl(line.image_url)
              return (
                <ListItem key={line.ingredient_id} alignItems="flex-start" sx={{ py: 1  }}>
                  <ListItemAvatar>
                    <Avatar
                      variant="rounded"
                      src={thumb}
                      alt={line.name}
                      slotProps={{
                        img: {
                          onError: (e: React.SyntheticEvent<HTMLImageElement>) => {
                            e.currentTarget.src = FALLBACK_INGREDIENT_IMG
                          },
                        },
                      }}
                      sx={{ width: 75, height: 75 }}
                    />
                  </ListItemAvatar>
                  <ListItemText primary={line.name} secondary={line.measure?.trim() || undefined} sx={{ py: 2.5  }}/>
                </ListItem>
              )
            })}
          </List>
        )}

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" component="h2" gutterBottom sx={{ color: 'text.primary' , fontWeight: 'bold' }}>
          Przygotowanie
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
          {recipe.instructions || 'Brak instrukcji.'}
        </Typography>
      </CardContent>
    </Card>
  )
}
