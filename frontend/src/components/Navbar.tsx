import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          MunchMate
        </Typography>
        <Button color="inherit" component={Link} to="/">Restaurants</Button>
        <Button color="inherit" component={Link} to="/order">Order</Button>
        <Button color="inherit" component={Link} to="/checkout">Checkout</Button>
        <Button color="inherit" component={Link} to="/loyalty">Loyalty</Button>
        <Button color="inherit" component={Link} to="/notifications">Notifications</Button>
        {user?.user_type === 'restaurant_manager' && (
          <Button color="inherit" component={Link} to="/admin">Admin</Button>
        )}
        <Button
          color="inherit"
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
