import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => (
  <AppBar position="static">
    <Toolbar>
      <Typography variant="h6" sx={{ flexGrow: 1 }}>
        MunchMate
      </Typography>
      <Button color="inherit" component={Link} to="/">Restaurants</Button>
      <Button color="inherit" component={Link} to="/order">Order</Button>
      <Button color="inherit" component={Link} to="/checkout">Checkout</Button>
      <Button color="inherit" component={Link} to="/notifications">Notifications</Button>
      <Button color="inherit" component={Link} to="/auth">Login/Register</Button>
    </Toolbar>
  </AppBar>
);

export default Navbar;
