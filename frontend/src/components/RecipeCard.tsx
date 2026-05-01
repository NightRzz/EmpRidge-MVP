import { Card, CardContent, CardMedia, Chip, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

const FALLBACK_IMAGE =
  'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'

type RecipeCardProps = {
  id: number
  title: string
  imageUrl: string | null
  matchedCount?: number
  totalCount?: number
  matchingRatio?: number
}

function ratioColor(ratio: number): 'success' | 'warning' | 'default' {
  if (ratio >= 75) return 'success'
  if (ratio >= 50) return 'warning'
  return 'default'
}

export default function RecipeCard({
  id,
  title,
  imageUrl,
  matchedCount,
  totalCount,
  matchingRatio,
}: RecipeCardProps) {
  const showRatio = matchingRatio !== undefined

  return (
    <Card
      component={RouterLink}
      to={`/recipe/${id}`}
      sx={{
        textDecoration: 'none',
        height: '100%',
        color: 'text.primary',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.22s ease, box-shadow 0.22s ease',
        '&:hover': {
          transform: 'translateY(-6px)',
          boxShadow: '0 20px 48px rgba(21,51,43,0.14)',
          borderColor: (t) => t.palette.primary.light,
        },
      }}
    >
      {showRatio && (
        <Chip
          label={`${matchingRatio.toFixed(0)}% (${matchedCount}/${totalCount})`}
          color={ratioColor(matchingRatio)}
          size="small"
          sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1, fontWeight: 600 }}
        />
      )}
      <CardMedia
        component="img"
        height="200"
        image={imageUrl || FALLBACK_IMAGE}
        alt={title}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
      </CardContent>
    </Card>
  )
}
