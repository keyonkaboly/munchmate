import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import Navbar from './components/Navbar';
import AuthPage from './pages/Auth';
import RestaurantsPage from './pages/Restaurants';
import RestaurantDetailPage from './pages/RestaurantDetail';
import OrderPage from './pages/Order';
import CheckoutPage from './pages/Checkout';
import NotificationsPage from './pages/Notifications';
import LoyaltyPage from './pages/Loyalty';
import AdminPage from './pages/Admin';
import DeliveryPage from './pages/Delivery';
import { useAuth } from './auth/AuthContext';

const RequireAuth: React.FC<{ isAuthenticated: boolean }> = ({ isAuthenticated }) => {
  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }
  return <Outlet />;
};

const LoadingScreen: React.FC = () => (
  <Box minHeight="100vh" display="flex" alignItems="center" justifyContent="center">
    <CircularProgress />
  </Box>
);

const AppRouter: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      {isAuthenticated && <Navbar />}
      <Routes>
        <Route
          path="/auth"
          element={isAuthenticated ? <Navigate to="/" replace /> : <AuthPage />}
        />

        <Route element={<RequireAuth isAuthenticated={isAuthenticated} />}>
          <Route path="/" element={<RestaurantsPage />} />
          <Route path="/restaurants/:id" element={<RestaurantDetailPage />} />
          <Route path="/order" element={<OrderPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/loyalty" element={<LoyaltyPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/delivery" element={<DeliveryPage />} />
        </Route>

        <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/auth'} replace />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;
