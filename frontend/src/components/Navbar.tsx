import React, { useEffect, useState, useCallback } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Badge,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

const BellIcon: React.FC = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
  </svg>
);

interface NotifEntry {
  is_read: boolean;
}

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);
  const [loggedIn, setLoggedIn] = useState(false);

  const refreshBadge = useCallback(async () => {
    try {
      const meRes = await api.get<{ id: number }>('/auth/me');
      setLoggedIn(true);
      const customerId = meRes.data.id;
      const notifRes = await api.get<{ notifications: NotifEntry[] }>(
        `/notifications/history/${customerId}`
      );
      const list = notifRes.data.notifications ?? [];
      setUnreadCount(list.filter((n) => !n.is_read).length);
    } catch {
      setLoggedIn(false);
      setUnreadCount(0);
    }
  }, []);

  useEffect(() => {
    void refreshBadge();
    const interval = setInterval(() => { void refreshBadge(); }, 30_000);
    return () => clearInterval(interval);
  }, [refreshBadge]);

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // ignore
    }
    setLoggedIn(false);
    setUnreadCount(0);
    navigate('/auth');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          MunchMate
        </Typography>
        <Button color="inherit" component={Link} to="/">Restaurants</Button>
        <Button color="inherit" component={Link} to="/order">Order</Button>
        <Button color="inherit" component={Link} to="/checkout">Checkout</Button>
        <Tooltip title={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}>
          <IconButton
            color="inherit"
            onClick={() => navigate('/notifications')}
            sx={{ mx: 0.5 }}
          >
            <Badge badgeContent={unreadCount > 0 ? unreadCount : undefined} color="error" max={99}>
              <BellIcon />
            </Badge>
          </IconButton>
        </Tooltip>
        {loggedIn ? (
          <Button color="inherit" onClick={() => { void handleLogout(); }}>Logout</Button>
        ) : (
          <Button color="inherit" component={Link} to="/auth">Login / Register</Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;