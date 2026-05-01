import { alpha, createTheme } from '@mui/material/styles'

const sageDeep = '#1e3d32'
const sage = '#2d5a47'
const sageLight = '#3d7260'
const cream = '#e4f8e7'
const paper = '#ffffff'
const terracotta = '#bc5c42'
const honey = '#c4a035'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: sage,
      dark: sageDeep,
      light: sageLight,
      contrastText: '#f8faf8',
    },
    secondary: {
      main: terracotta,
      light: '#d67d66',
      dark: '#8f3f2c',
      contrastText: '#fffefb',
    },
    background: {
      default: cream,
      paper: paper,
    },
    text: {
      primary: '#1c1917',
      secondary: '#57534e',
    },
    divider: alpha(sageDeep, 0.1),
    success: {
      main: sageLight,
      contrastText: '#f8faf8',
    },
  },
  typography: {
    fontFamily: '"DM Sans", "Segoe UI", system-ui, sans-serif',
    h1: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    h2: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    h3: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    h4: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    h5: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    h6: { fontFamily: '"Fraunces", Georgia, "Times New Roman", serif', fontWeight: 600 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600, letterSpacing: 0.02 },
    body1: { lineHeight: 1.65 },
    body2: { lineHeight: 1.6 },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          scrollBehavior: 'smooth',
        },
        body: {
          backgroundAttachment: 'fixed',
          backgroundImage: `linear-gradient(175deg, ${alpha(honey, 0.07)} 0%, transparent 42%), linear-gradient(210deg, ${alpha(sage, 0.05)} 0%, transparent 38%)`,
        },
      },
    },
    MuiAppBar: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: `linear-gradient(118deg, ${alpha(sageDeep, 0.97)} 0%, ${alpha(sage, 0.95)} 42%, ${alpha('#163028', 0.98)} 100%)`,
          backdropFilter: 'blur(12px)',
          borderBottom: `1px solid ${alpha('#fff', 0.1)}`,
          boxShadow: `0 8px 32px ${alpha('#06120e', 0.45)}`,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
      },
      variants: [
        {
          props: { variant: 'contained', color: 'primary' },
          style: {
            boxShadow: `0 2px 8px ${alpha(sage, 0.35)}`,
            '&:hover': {
              boxShadow: `0 4px 14px ${alpha(sage, 0.45)}`,
            },
          },
        },
      ],
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          border: `1px solid ${alpha(sageDeep, 0.08)}`,
          boxShadow: `0 2px 8px ${alpha('#0c1a14', 0.04)}, 0 12px 40px ${alpha(sageDeep, 0.06)}`,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: ({ theme }) => ({
          ...(theme.palette.mode === 'light' && {
            backgroundImage: 'none',
          }),
        }),
        outlined: {
          borderColor: alpha(sageDeep, 0.12),
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: ({ theme }) => ({
          '& .MuiTableCell-root': {
            bgcolor: alpha(theme.palette.primary.main, 0.06),
            color: theme.palette.text.primary,
            fontWeight: 700,
          },
        }),
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: ({ theme }) => ({
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: alpha(theme.palette.primary.main, 0.45),
          },
        }),
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 18,
          border: `1px solid ${alpha(sageDeep, 0.08)}`,
          boxShadow: `0 24px 80px ${alpha('#06120e', 0.18)}`,
        },
      },
    },
  },
})
