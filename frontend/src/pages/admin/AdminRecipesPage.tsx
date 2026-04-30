import { Alert, Typography } from '@mui/material'

export default function AdminRecipesPage() {
  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Recipes
      </Typography>
      <Alert severity="info">Widok CRUD przepisów będzie realizowany w kolejnych issue.</Alert>
    </>
  )
}
