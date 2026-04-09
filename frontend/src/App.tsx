import { Box } from '@mui/material';
import AppRouter from './AppRouter';

function App() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'fixed',
          inset: 'auto auto 14% -8%',
          width: 280,
          height: 280,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(212, 126, 48, 0.14), transparent 70%)',
          pointerEvents: 'none',
          filter: 'blur(10px)',
        },
        '&::after': {
          content: '""',
          position: 'fixed',
          inset: '10% -6% auto auto',
          width: 320,
          height: 320,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(130, 94, 52, 0.12), transparent 72%)',
          pointerEvents: 'none',
          filter: 'blur(14px)',
        },
      }}
    >
      <AppRouter />
    </Box>
  );
}

export default App;
