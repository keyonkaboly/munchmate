import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CssBaseline, ThemeProvider, alpha, createTheme } from '@mui/material'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './auth/AuthContext.tsx'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#D47E30',
      light: '#E39C5E',
      dark: '#B5641D',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#825E34',
      light: '#9E7A4E',
      dark: '#634626',
      contrastText: '#ffffff',
    },
    background: {
      default: '#FDFBF5',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2E241A',
      secondary: '#64523F',
    },
    success: {
      main: '#2F8F5B',
    },
    warning: {
      main: '#D47E30',
    },
    error: {
      main: '#C9442F',
    },
  },
  shape: {
    borderRadius: 20,
  },
  typography: {
    fontFamily: `Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
    h4: {
      fontWeight: 800,
      letterSpacing: '-0.03em',
    },
    h5: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h6: {
      fontWeight: 700,
    },
    button: {
      fontWeight: 700,
      textTransform: 'none',
      letterSpacing: '0.01em',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          minHeight: '100vh',
          background:
            'linear-gradient(180deg, #fdfbf5 0%, #f7f1e6 100%)',
          color: '#2E241A',
        },
        '::selection': {
          backgroundColor: alpha('#D47E30', 0.2),
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: '#825E34',
          backdropFilter: 'blur(18px)',
          boxShadow: '0 10px 22px rgba(80, 56, 28, 0.22)',
          border: 'none',
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: '76px',
          gap: '0.5rem',
          flexWrap: 'wrap',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          paddingInline: '1.1rem',
          paddingBlock: '0.72rem',
          boxShadow: '0 6px 16px rgba(99, 70, 38, 0.16)',
          transition: 'transform 180ms ease, box-shadow 180ms ease, background-color 180ms ease, color 180ms ease, border-color 180ms ease',
          '&:hover': {
            transform: 'translateY(-2px) scale(1.03)',
            boxShadow: '0 12px 24px rgba(99, 70, 38, 0.22)',
          },
        },
        contained: {
          background: '#D47E30',
          '&:hover': {
            background: '#B5641D',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          color: '#2E241A',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            borderWidth: '1.5px',
          },
        },
        text: {
          boxShadow: 'none',
          '&:hover': {
            backgroundColor: alpha('#FFFFFF', 0.18),
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(18px)',
          border: '1px solid rgba(212, 126, 48, 0.18)',
          boxShadow: '0 14px 34px rgba(87, 63, 36, 0.12)',
          transition: 'transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            borderColor: 'rgba(212, 126, 48, 0.34)',
            boxShadow: '0 20px 40px rgba(87, 63, 36, 0.18)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 18,
          backgroundColor: 'rgba(255, 255, 255, 0.92)',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 18,
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          backgroundColor: 'rgba(212, 126, 48, 0.15)',
          fontWeight: 600,
        },
      },
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>,
)
