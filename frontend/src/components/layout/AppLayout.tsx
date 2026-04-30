import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material'
import { Link as RouterLink, Outlet } from 'react-router-dom'

export default function AppLayout() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="sticky" color="primary" elevation={1}>
        <Toolbar>
          <Typography component={RouterLink} to="/" variant="h6" sx={{ color: 'inherit', textDecoration: 'none', flexGrow: 1 }}>
            EmpRidge MVP
          </Typography>
          <Button component={RouterLink} to="/" color="inherit">
            Galeria
          </Button>
          <Button component={RouterLink} to="/admin/recipes" color="inherit">
            Admin Recipes
          </Button>
          <Button component={RouterLink} to="/admin/ingredients" color="inherit">
            Admin Ingredients
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  )
}
