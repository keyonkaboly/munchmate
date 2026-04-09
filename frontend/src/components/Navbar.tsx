import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const Navbar: React.FC = () => {
  const { logout } = useAuth();

  const navButtonSx = {
    color: 'rgba(255,255,255,0.92)',
    borderRadius: 999,
    px: 2,
    '&:hover': {
      color: '#ffffff',
      backgroundColor: 'rgba(255,255,255,0.16)',
      transform: 'translateY(-2px) scale(1.04)',
      boxShadow: '0 10px 24px rgba(43, 27, 11, 0.2)',
    },
  } as const;

  const logoutButtonSx = {
    borderColor: 'rgba(255,255,255,0.34)',
    color: '#2E241A',
    backgroundColor: '#FFF7EA',
    fontWeight: 800,
    '&:hover': {
      borderColor: '#ffffff',
      backgroundColor: '#ffffff',
      color: '#2E241A',
      transform: 'translateY(-2px) scale(1.04)',
      boxShadow: '0 10px 24px rgba(43, 27, 11, 0.24)',
    },
  } as const;

  return (
    <AppBar position="sticky" sx={{ top: 0, borderRadius: 0, width: '100%' }}>
      <Toolbar sx={{ px: { xs: 1, md: 2 }, maxWidth: 1280, width: '100%', mx: 'auto' }}>
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 800, letterSpacing: '-0.03em' }}>
          MunchMate
        </Typography>
        <Button color="inherit" component={Link} to="/" sx={navButtonSx}>Restaurants</Button>
        <Button color="inherit" component={Link} to="/order" sx={navButtonSx}>Order</Button>
        <Button color="inherit" component={Link} to="/checkout" sx={navButtonSx}>Checkout</Button>
        <Button color="inherit" component={Link} to="/loyalty" sx={navButtonSx}>Loyalty</Button>
        <Button color="inherit" component={Link} to="/notifications" sx={navButtonSx}>Notifications</Button>
        <Button
          color="inherit"
          variant="outlined"
          sx={logoutButtonSx}
          onClick={async () => {
            await logout();
          }}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
