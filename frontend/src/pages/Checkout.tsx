import React, { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  Divider,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import api from '../api';
import { useAuth } from '../auth/AuthContext';
import { ACTIVE_ORDER_STORAGE_KEY } from '../customerSession';

interface GroupedOrder {
  order_id: string;
  restaurant_id: number;
  food_items?: string[];
}

interface CustomerOrdersForNotify {
  current_orders: GroupedOrder[];
  past_orders: GroupedOrder[];
}

interface MenuItemRow {
  food_item: string;
  price: number;
}

interface RestaurantDetail {
  id: number;
  menu_items: MenuItemRow[];
}

async function resolveRestaurantForOrder(orderId: string, customerId: number): Promise<number | null> {
  try {
    const res = await api.get<CustomerOrdersForNotify>(`/orders/customer/${customerId}`);
    const all = [...(res.data.current_orders || []), ...(res.data.past_orders || [])];
    return all.find((o) => o.order_id === orderId)?.restaurant_id ?? null;
  } catch {
    return null;
  }
}

async function firePostCheckoutNotifications(
  orderId: string,
  customerId: number,
  restaurantId: number | null
) {
  const customerQs = new URLSearchParams({
    order_id: orderId,
    customer_id: String(customerId),
  }).toString();
  const tasks = [
    api.post(`/notifications/order-confirmed?${customerQs}`),
    api.post(`/notifications/delivery-status?${customerQs}`),
  ];
  if (restaurantId != null) {
    const incomingQs = new URLSearchParams({
      order_id: orderId,
      restaurant_id: String(restaurantId),
    }).toString();
    tasks.push(api.post(`/notifications/incoming-order?${incomingQs}`));
  }
  await Promise.allSettled(tasks);
}

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

interface LoyaltySummary {
  points: number;
  reward_percent: number;
}

interface LoyaltyApplyResponse {
  applied: boolean;
  reason?: string;
  discounted_total?: number;
}

const extractApiErrorMessage = (err: unknown): string => {
  if (!(err instanceof Object) || !('response' in err)) {
    return err instanceof Error ? err.message : '';
  }
  const response = (err as { response?: { data?: unknown } }).response;
  const data = response?.data;
  if (data instanceof Object) {
    const maybe = data as {
      detail?: string | Array<{ msg?: string }>;
      message?: string;
      error?: string;
    };
    if (typeof maybe.detail === 'string' && maybe.detail.trim()) return maybe.detail;
    if (Array.isArray(maybe.detail) && maybe.detail.length > 0) {
      const first = maybe.detail[0]?.msg;
      if (typeof first === 'string' && first.trim()) return first;
    }
    if (typeof maybe.message === 'string' && maybe.message.trim()) return maybe.message;
    if (typeof maybe.error === 'string' && maybe.error.trim()) return maybe.error;
  }
  return err instanceof Error ? err.message : '';
};

const CheckoutPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [orderId, setOrderId] = useState(() => sessionStorage.getItem(ACTIVE_ORDER_STORAGE_KEY) ?? '');
  const [cardNumber, setCardNumber] = useState('');
  const [totals, setTotals] = useState<CheckoutTotals | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [paymentMessage, setPaymentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [foodItems, setFoodItems] = useState<string[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItemRow[]>([]);
  const [useLoyalty, setUseLoyalty] = useState(false);
  const [loyaltySummary, setLoyaltySummary] = useState<LoyaltySummary | null>(null);
  const [loadingLoyalty, setLoadingLoyalty] = useState(false);

  const mapLoyaltyReason = (reason?: string): string => {
    if (reason === 'no_rewards_available') return "You don't have loyalty available right now.";
    if (reason === 'order_not_found') return 'Order not found for loyalty.';
    if (reason === 'order_not_owned_by_customer') return 'This order is not yours.';
    if (reason === 'order_total_invalid') return 'This order total is not eligible for loyalty.';
    return 'Could not apply loyalty right now.';
  };

  const displayedTotal = useMemo(() => {
    if (!totals) return 0;
    if (!useLoyalty || !loyaltySummary) return totals.total_cost;
    return Number((totals.total_cost * (1 - loyaltySummary.reward_percent / 100)).toFixed(2));
  }, [totals, useLoyalty, loyaltySummary]);

  useEffect(() => {
    const loadLoyalty = async () => {
      if (!user?.id) { setLoyaltySummary(null); return; }
      setLoadingLoyalty(true);
      try {
        const res = await api.get<LoyaltySummary>(`/loyalty/${user.id}`);
        setLoyaltySummary(res.data);
      } catch {
        setLoyaltySummary(null);
      } finally {
        setLoadingLoyalty(false);
      }
    };
    void loadLoyalty();
  }, [user?.id]);

  useEffect(() => {
    if (!orderId.trim()) { setTotals(null); return; }
    const calculate = async () => {
      setLoading(true);
      setError('');
      setTotals(null);
      setPaymentSuccess(false);
      setPaymentMessage('');
      setFoodItems([]);
      setMenuItems([]);
      try {
        const res = await api.post<CheckoutTotals>('/checkout/calculate', { order_id: orderId.trim() });
        setTotals(res.data);
        if (user?.id) {
          const ordersRes = await api.get<CustomerOrdersForNotify>(`/orders/customer/${user.id}`);
          const all = [...(ordersRes.data.current_orders || []), ...(ordersRes.data.past_orders || [])];
          const found = all.find((o) => o.order_id === orderId.trim());
          setFoodItems(found?.food_items ?? []);
          if (found?.restaurant_id) {
            const menuRes = await api.get<RestaurantDetail>(`/restaurants/${found.restaurant_id}`);
            setMenuItems(menuRes.data.menu_items ?? []);
          }
        }
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
  }, [orderId, user?.id]);

  const handlePay = async () => {
    if (!totals || !cardNumber.trim()) return;
    const normalizedCard = cardNumber.replace(/\s+/g, '');
    if (!/^\d{16}$/.test(normalizedCard)) {
      setError('Card number must be exactly 16 digits.');
      return;
    }
    setLoading(true);
    setError('');
    setPaymentMessage('');
    try {
      await api.post(`/checkout/orders/${orderId.trim()}/place`);
      let finalAmount = totals.total_cost;
      if (useLoyalty) {
        if (!user?.id) { setError('You must be logged in to apply loyalty.'); return; }
        let loyaltyRes;
        try {
          loyaltyRes = await api.post<LoyaltyApplyResponse>('/loyalty/apply', {
            customer_id: user.id,
            combined_order_id: orderId.trim(),
          });
        } catch (loyaltyErr: unknown) {
          const loyaltyDetail = extractApiErrorMessage(loyaltyErr);
          setError(loyaltyDetail
            ? `Loyalty validation failed: ${loyaltyDetail}. Uncheck loyalty to continue with normal payment.`
            : 'Loyalty validation failed. Uncheck loyalty to continue with normal payment.');
          return;
        }
        if (!loyaltyRes.data.applied) {
          setError(`${mapLoyaltyReason(loyaltyRes.data.reason)} Uncheck loyalty to continue with normal payment.`);
          return;
        }
        if (typeof loyaltyRes.data.discounted_total !== 'number') {
          setError('Loyalty validation failed. Uncheck loyalty to continue with normal payment.');
          return;
        }
        finalAmount = loyaltyRes.data.discounted_total;
      }
      const paymentRes = await api.post<PaymentResponse>('/payments/checkout', {
        order_id: orderId.trim(),
        total_cost: finalAmount,
        card_number: normalizedCard,
      });
      setPaymentSuccess(paymentRes.data.success);
      setPaymentMessage(paymentRes.data.message);
      if (paymentRes.data.success) {
        sessionStorage.removeItem(ACTIVE_ORDER_STORAGE_KEY);
        sessionStorage.setItem('munchmate_paid_order_id', orderId.trim());
        if (user?.id != null) {
          const rid = await resolveRestaurantForOrder(orderId.trim(), user.id);
          await firePostCheckoutNotifications(orderId.trim(), user.id, rid);
        }
      } else {
        setError(paymentRes.data.message || 'Payment failed. Please try again.');
      }
    } catch (err: unknown) {
      const detail = extractApiErrorMessage(err);
      setError(detail || 'Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelWithRefund = async () => {
    setLoading(true);
    setError('');
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
        <Alert severity={paymentSuccess ? 'success' : 'info'} sx={{ mb: 2 }}>
          {paymentMessage}
          {paymentSuccess && (
            <Button component={RouterLink} to="/notifications" size="small" sx={{ ml: 1 }}>
              View notifications
            </Button>
          )}
        </Alert>
      )}

      <TextField
        label="Order ID"
        fullWidth
        value={orderId}
        onChange={(e) => {
          setOrderId(e.target.value);
          setPaymentSuccess(false);
          setPaymentMessage('');
          setError('');
          setUseLoyalty(false);
        }}
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
              {foodItems.length > 0 && (
                <>
                  {foodItems.map((item, idx) => {
                    const match = menuItems.find((m) => m.food_item === item);
                    return (
                      <Stack key={idx} direction="row" justifyContent="space-between">
                        <Typography variant="body2">{item}</Typography>
                        <Typography variant="body2">{match ? `$${match.price.toFixed(2)}` : '—'}</Typography>
                      </Stack>
                    );
                  })}
                  <Divider />
                </>
              )}
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
                <Typography fontWeight="bold">
                  {useLoyalty && loyaltySummary ? (
                    <>
                      <Box component="span" sx={{ textDecoration: 'line-through', mr: 1 }}>
                        ${totals.total_cost.toFixed(2)}
                      </Box>
                      <Box component="span" color="success.main">
                        ${displayedTotal.toFixed(2)}
                      </Box>
                    </>
                  ) : (
                    `$${totals.total_cost.toFixed(2)}`
                  )}
                </Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      )}

      {totals && !paymentSuccess && (
        <>
          <FormControlLabel
            control={
              <Checkbox
                checked={useLoyalty}
                onChange={(event) => { setUseLoyalty(event.target.checked); setError(''); setPaymentMessage(''); }}
                disabled={loading}
              />
            }
            label="Apply loyalty reward (if available)"
            sx={{ mb: 1 }}
          />
          {loadingLoyalty ? (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Loading loyalty info...</Typography>
          ) : loyaltySummary ? (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Loyalty points: {loyaltySummary.points}. Eligible rewards apply {loyaltySummary.reward_percent}% off.
            </Typography>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Loyalty status unavailable right now.</Typography>
          )}
          {useLoyalty && (
            <Alert severity="info" sx={{ mb: 2 }}>
              This is an estimate from your loyalty summary. Final loyalty eligibility is verified when you click Pay.
            </Alert>
          )}
          <TextField
            label="Card number"
            fullWidth
            value={cardNumber}
            onChange={(e) => setCardNumber(e.target.value)}
            placeholder="4111111111111111"
            helperText="Enter exactly 16 digits (test card: 4111111111111111)."
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading || !cardNumber.trim()}
            onClick={() => { void handlePay(); }}
          >
            {loading ? <CircularProgress size={22} color="inherit" /> : `Pay $${displayedTotal.toFixed(2)}`}
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
            sx={{ mb: 1 }}
          >
            Cancel with Refund
          </Button>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={() => navigate('/delivery')}
          >
            View Delivery
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default CheckoutPage;