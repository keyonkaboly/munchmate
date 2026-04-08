import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Box,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import api from '../api';

interface CheckoutData {
  order_id: string;
  subtotal: number;
  tax: number;
  delivery_cost: number;
  total_cost: number;
}

const CheckoutPage: React.FC = () => {
  const [orderId, setOrderId] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [checkoutData, setCheckoutData] = useState<CheckoutData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Get order ID from URL params or localStorage (you might want to pass it from previous page)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const orderIdFromUrl = urlParams.get('orderId');
    if (orderIdFromUrl) {
      setOrderId(orderIdFromUrl);
      calculateCheckout(orderIdFromUrl);
    }
  }, []);

  const calculateCheckout = async (orderId: string) => {
    if (!orderId.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await api.post('/checkout/calculate', {
        order_id: orderId
      });
      setCheckoutData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to calculate checkout totals');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = () => {
    calculateCheckout(orderId);
  };

  const handlePlaceOrder = async () => {
    if (!checkoutData || !cardNumber.trim()) {
      setError('Please enter order ID and card number');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // First place the order
      const placeResponse = await api.post(`/checkout/orders/${orderId}/place`);
      setCheckoutData(placeResponse.data);

      // Note: Payment processing endpoint was removed, so we'll just show success
      setSuccess('Order placed successfully! Payment would be processed here.');

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Checkout & Payment
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Order Details */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Details
              </Typography>

              <TextField
                fullWidth
                label="Order ID"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                margin="normal"
                required
              />

              <Button
                variant="outlined"
                onClick={handleCalculate}
                disabled={loading || !orderId.trim()}
                sx={{ mt: 1 }}
              >
                {loading ? <CircularProgress size={20} /> : 'Calculate Totals'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Summary
              </Typography>

              {checkoutData ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Subtotal:</Typography>
                    <Typography>{formatCurrency(checkoutData.subtotal)}</Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Tax:</Typography>
                    <Typography>{formatCurrency(checkoutData.tax)}</Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Delivery Cost:</Typography>
                    <Typography>{formatCurrency(checkoutData.delivery_cost)}</Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">Total:</Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(checkoutData.total_cost)}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography color="text.secondary">
                  Enter order ID and click "Calculate Totals" to see summary
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Payment Information */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Payment Information
              </Typography>

              <TextField
                fullWidth
                label="Card Number"
                value={cardNumber}
                onChange={(e) => setCardNumber(e.target.value)}
                margin="normal"
                placeholder="Enter 16-digit card number"
                required
                inputProps={{ maxLength: 16 }}
              />

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={handlePlaceOrder}
                  disabled={loading || !checkoutData || !cardNumber.trim()}
                  fullWidth
                >
                  {loading ? <CircularProgress size={24} /> : 'Place Order & Pay'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CheckoutPage;
