import React, { useEffect, useState } from 'react';
import {
  Box, Typography, TextField, Button, Alert, CircularProgress,
  Card, CardContent, Divider, Stack,
} from '@mui/material';
import api from '../api';

const ACTIVE_ORDER_KEY = 'munchmate_active_order_id';

interface CheckoutTotals {
  order_id: string;
  subtotal: number;
  tax: number;
  delivery_cost: number;
  total_cost: number;
}

interface PaymentResponse {
  success: boolean;
  message: string;
}

const CheckoutPage: React.FC = () => {
  const [orderId, setOrderId] = useState(() => sessionStorage.getItem(ACTIVE_ORDER_KEY) ?? '');
  const [cardNumber, setCardNumber] = useState('');
  const [totals, setTotals] = useState<CheckoutTotals | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [paymentMessage, setPaymentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderId.trim()) { setTotals(null); return; }
    const calculate = async () => {
      setLoading(true); setError(''); setTotals(null);
      setPaymentSuccess(false); setPaymentMessage('');
      try {
        const res = await api.post<CheckoutTotals>('/checkout/calculate', { order_id: orderId.trim() });
        setTotals(res.data);
      } catch (err: unknown) {
        const detail =
          err instanceof Object && 'response' in err &&
          err.response instanceof Object && 'data' in err.response &&
          err.response.data instanceof Object && 'detail' in err.response.data
            ? (err.response.data as { detail: string }).detail : '';
        setError(typeof detail === 'string' && detail ? detail : 'Could not calculate totals. Check the order ID.');
      } finally {
        setLoading(false);
      }
    };
    void calculate();
  }, [orderId]);

  const handlePay = async () => {
    if (!totals || !cardNumber.trim()) return;
    setLoading(true); setError('');
    try {
      await api.post(`/checkout/orders/${orderId.trim()}/place`);
      const res = await api.post<PaymentResponse>('/payments/checkout', {
        order_id: orderId.trim(),
        total_cost: totals.total_cost,
        card_number: cardNumber.trim(),
      });
      setPaymentSuccess(res.data.success);
      setPaymentMessage(res.data.message);
      if (res.data.success) sessionStorage.removeItem(ACTIVE_ORDER_KEY);
    } catch (err: unknown) {
      const detail =
        err instanceof Object && 'response' in err &&
        err.response instanceof Object && 'data' in err.response &&
        err.response.data instanceof Object && 'detail' in err.response.data
          ? (err.response.data as { detail: string }).detail : '';
      setError(typeof detail === 'string' && detail ? detail : 'Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelWithRefund = async () => {
    setLoading(true); setError('');
    try {
      await api.post(`/orders/${orderId.trim()}/cancel-with-refund`);
      setPaymentSuccess(false);
      setPaymentMessage('Order canceled and refund issued.');
    } catch (err: unknown) {
      const detail =
        err instanceof Object && 'response' in err &&
        err.response instanceof Object && 'data' in err.response &&
        err.response.data instanceof Object && 'detail' in err.response.data
          ? (err.response.data as { detail: string }).detail : '';
      setError(typeof detail === 'string' && detail ? detail : 'Refund failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3} maxWidth={540} mx="auto">
      <Typography variant="h4" mb={2}>Checkout</Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {paymentMessage && (
        <Alert severity={paymentSuccess ? 'success' : 'error'} sx={{ mb: 2 }}>{paymentMessage}</Alert>
      )}

      <TextField
        label="Order ID"
        fullWidth
        value={orderId}
        onChange={(e) => { setOrderId(e.target.value); setPaymentSuccess(false); setPaymentMessage(''); }}
        helperText="Auto-filled when you create an order, or paste it manually."
        sx={{ mb: 2 }}
      />

      {loading && !totals && (
        <Box display="flex" justifyContent="center" py={2}><CircularProgress size={28} /></Box>
      )}

      {totals && (
        <Card variant="outlined" sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" mb={1}>Order summary</Typography>
            <Stack spacing={0.5}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Subtotal</Typography>
                <Typography variant="body2">${totals.subtotal.toFixed(2)}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Tax</Typography>
                <Typography variant="body2">${totals.tax.toFixed(2)}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Delivery</Typography>
                <Typography variant="body2">${totals.delivery_cost.toFixed(2)}</Typography>
              </Stack>
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography fontWeight="bold">Total</Typography>
                <Typography fontWeight="bold">${totals.total_cost.toFixed(2)}</Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      )}

      {totals && !paymentSuccess && (
        <>
          <TextField
            label="Card number"
            fullWidth
            value={cardNumber}
            onChange={(e) => setCardNumber(e.target.value)}
            placeholder="4111111111111111"
            helperText="Any 16-digit number works in this demo."
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading || !cardNumber.trim()}
            onClick={() => { void handlePay(); }}
          >
            {loading ? <CircularProgress size={22} color="inherit" /> : `Pay $${totals.total_cost.toFixed(2)}`}
          </Button>
        </>
      )}

      {paymentSuccess && (
        <Box mt={2}>
          <Button
            variant="outlined"
            color="error"
            fullWidth
            disabled={loading}
            onClick={() => { void handleCancelWithRefund(); }}
          >
            Cancel with Refund
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default CheckoutPage;