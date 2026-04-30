import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6f4e37',
    },
    secondary: {
      main: '#ffa726',
    },
    background: {
      default: '#f7f7f7',
    },
  },
  shape: {
    borderRadius: 12,
  },
})
