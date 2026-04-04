import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import AuthPage from './pages/Auth';
import RestaurantsPage from './pages/Restaurants';
import RestaurantDetailPage from './pages/RestaurantDetail';
import OrderPage from './pages/Order';
import CheckoutPage from './pages/Checkout';
import NotificationsPage from './pages/Notifications';

const AppRouter: React.FC = () => (
  <Router>
    <Navbar />
    <Routes>
      <Route path="/" element={<RestaurantsPage />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/restaurants/:id" element={<RestaurantDetailPage />} />
      <Route path="/order" element={<OrderPage />} />
      <Route path="/checkout" element={<CheckoutPage />} />
      <Route path="/notifications" element={<NotificationsPage />} />
    </Routes>
  </Router>
);

export default AppRouter;
