import ArticleIcon from '@mui/icons-material/Article';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import RestaurantMenuRoundedIcon from '@mui/icons-material/RestaurantMenuRounded'
import MenuBookIcon from '@mui/icons-material/MenuBook';
import { alpha, AppBar, Box, Button, Container, Stack, Toolbar, Typography } from '@mui/material'
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'

export default function AppLayout() {
  const { pathname } = useLocation()

  const galleryActive = pathname === '/' || pathname.startsWith('/recipe/')
  const adminRecipesActive = pathname.startsWith('/admin/recipes')
  const adminIngredientsActive = pathname.startsWith('/admin/ingredients')

  const pill = (active: boolean) => ({
    borderRadius: 2,
    px: 1.25,
    py: 0.75,
    minHeight: 40,
    color: alpha('#fdfcfa', active ? 1 : 0.78),
    bgcolor: active ? alpha('#fff', 0.14) : 'transparent',
    border: `1px solid ${alpha('#fff', active ? 0.22 : 0)}`,
    boxShadow: active ? `0 2px 12px ${alpha('#000', 0.22)}` : 'none',
    transition: 'background-color 160ms ease, color 160ms ease, border-color 160ms ease, box-shadow 160ms ease',
    '&:hover': {
      bgcolor: alpha('#fff', active ? 0.18 : 0.1),
      color: '#fdfcfa',
    },
  })

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
      <AppBar position="sticky" color="primary">
        <Toolbar
          sx={{
            maxWidth: 'lg',
            width: '100%',
            mx: 'auto',
            px: { xs: 2, sm: 3 },
            flexWrap: 'wrap',
            rowGap: 1,
            py: { xs: 2, md: 1.25 },
            columnGap: 1,
          }}
          disableGutters
        >
          <Box
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              minWidth: 0,
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            <Stack direction="row" spacing={2} sx={{ alignItems: 'center', minWidth: 0 }}>
              <Box
                aria-hidden
                sx={{
                  width: 42,
                  height: 42,
                  borderRadius: 2,
                  display: 'grid',
                  placeItems: 'center',
                  flexShrink: 0,
                  bgcolor: alpha('#ffb84d', 0.92),
                  color: '#1a3329',
                  boxShadow: `0 4px 14px ${alpha('#ffb84d', 0.45)}`,
                }}
              >
                <RestaurantMenuRoundedIcon sx={{ fontSize: 26 }} />
              </Box>
              <Box sx={{ minWidth: 0 }}>
                <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
                  <Typography variant="h6" component="span" noWrap sx={{ letterSpacing: 0.03, fontWeight: 700 }}>
                    EmpRidge
                  </Typography>

                </Stack>
                <Typography variant="caption" sx={{ display: 'block', opacity: 0.74, mt: -0.25 }}>
                  Szukaj przepis po składnikach · opróżnij lodówkę!
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={0.5}
            sx={{
              ml: 'auto',
              alignItems: { xs: 'stretch', sm: 'center' },
              bgcolor: { sm: alpha('#000', 0.12) },
              borderRadius: 2,
              p: { sm: 0.5 },
              border: { sm: `1px solid ${alpha('#fff', 0.12)}` },
            }}
          >
            <Button
              component={RouterLink}
              to="/"
              startIcon={<MenuBookIcon fontSize="small" />}
              disableElevation
              sx={pill(galleryActive)}
            >
              Galeria
            </Button>
            <Button
              component={RouterLink}
              to="/admin/recipes"
              startIcon={<ArticleIcon fontSize="small" />}
              disableElevation
              sx={pill(adminRecipesActive)}
            >
              Przepisy
            </Button>
            <Button
              component={RouterLink}
              to="/admin/ingredients"
              startIcon={<Inventory2OutlinedIcon fontSize="small" />}
              disableElevation
              sx={pill(adminIngredientsActive)}
            >
              Składniki
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Container
        maxWidth="lg"
        component="main"
        sx={{
          flex: 1,
          py: { xs: 3, md: 4 },
          pb: { xs: 6, md: 8 },
        }}
      >
        <Outlet />
      </Container>

      <Box
        component="footer"
        sx={{
          py: 2,
          textAlign: 'center',
          color: 'text.secondary',
          typography: 'caption',
          borderTop: (t) => `1px solid ${alpha(t.palette.primary.dark, 0.08)}`,
          bgcolor: (t) => alpha(t.palette.background.paper, 0.75),
          backdropFilter: 'blur(8px)',
        }}
      >
        EmpRidge — przeglądaj i zarządzaj przepisami
      </Box>
    </Box>
  )
}
