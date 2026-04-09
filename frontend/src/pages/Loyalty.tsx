import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import api from '../api';
import { useAuth } from '../auth/AuthContext';

const CUSTOMER_STORAGE_KEY = 'munchmate_customer_id';
const LOYALTY_DISCOUNT_STORAGE_KEY = 'munchmate_loyalty_discounts';

interface StoredLoyaltyDiscount {
  order_total: number;
  discount_percent: number;
  discount_amount: number;
  discounted_total: number;
  applied_at: string;
}

interface LoyaltySummary {
  points: number;
  reward_percent: number;
}

interface LoyaltyApplyResponse {
  applied: boolean;
  reason?: string;
  combined_order_id?: string;
  order_total?: number;
  discount_percent?: number;
  discount_amount?: number;
  discounted_total?: number;
}

function readStoredCustomerId(): number {
  const raw = sessionStorage.getItem(CUSTOMER_STORAGE_KEY);
  if (!raw) return 1;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
}

const LoyaltyPage: React.FC = () => {
  const { user } = useAuth();
  const [customerId, setCustomerId] = useState<number>(readStoredCustomerId);
  const [orderId, setOrderId] = useState('');
  const [summary, setSummary] = useState<LoyaltySummary | null>(null);
  const [applyResult, setApplyResult] = useState<LoyaltyApplyResponse | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [applyingReward, setApplyingReward] = useState(false);
  const [error, setError] = useState('');

  const persistDiscount = (order: string, data: LoyaltyApplyResponse) => {
    if (
      data.discounted_total === undefined ||
      data.discount_amount === undefined ||
      data.discount_percent === undefined ||
      data.order_total === undefined
    ) {
      return;
    }

    const raw = sessionStorage.getItem(LOYALTY_DISCOUNT_STORAGE_KEY);
    const parsed = raw ? (JSON.parse(raw) as Record<string, StoredLoyaltyDiscount>) : {};

    parsed[order] = {
      order_total: data.order_total,
      discount_percent: data.discount_percent,
      discount_amount: data.discount_amount,
      discounted_total: data.discounted_total,
      applied_at: new Date().toISOString(),
    };

    sessionStorage.setItem(LOYALTY_DISCOUNT_STORAGE_KEY, JSON.stringify(parsed));
  };

  const goToCheckoutWithOrder = (oid: string | undefined) => {
    if (!oid) {
      return;
    }
    sessionStorage.setItem('munchmate_active_order_id', oid);
    window.location.href = '/checkout';
  };

  React.useEffect(() => {
    if (user?.id) {
      setCustomerId(user.id);
      sessionStorage.setItem(CUSTOMER_STORAGE_KEY, String(user.id));
    }
  }, [user?.id]);

  const fetchSummary = async () => {
    setLoadingSummary(true);
    setError('');
    setApplyResult(null);
    try {
      sessionStorage.setItem(CUSTOMER_STORAGE_KEY, String(customerId));
      const response = await api.get<LoyaltySummary>(`/loyalty/${customerId}`);
      setSummary(response.data);
    } catch (fetchError: unknown) {
      const detail = (fetchError as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setSummary(null);
      setError(typeof detail === 'string' ? detail : 'Failed to load loyalty summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const applyReward = async () => {
    if (!orderId.trim()) {
      setError('Enter an order ID before applying a reward.');
      return;
    }

    setApplyingReward(true);
    setError('');
    setApplyResult(null);
    try {
      const response = await api.post<LoyaltyApplyResponse>('/loyalty/apply', {
        customer_id: customerId,
        combined_order_id: orderId.trim(),
      });
      setApplyResult(response.data);

      if (response.data.applied) {
        persistDiscount(orderId.trim(), response.data);
      }

      await fetchSummary();
    } catch (applyError: unknown) {
      const detail = (applyError as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to apply loyalty reward');
    } finally {
      setApplyingReward(false);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>
        Loyalty Rewards
      </Typography>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={2}>
        <TextField
          label="Customer ID"
          type="number"
          value={customerId}
          onChange={(event) => {
            const value = Number.parseInt(event.target.value, 10);
            setCustomerId(Number.isFinite(value) && value > 0 ? value : 1);
          }}
          sx={{ maxWidth: 220 }}
          helperText={user ? 'Auto-filled from your logged-in account.' : undefined}
        />
        <Button variant="contained" onClick={fetchSummary} disabled={loadingSummary}>
          {loadingSummary ? <CircularProgress size={22} /> : 'Load rewards'}
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" mb={2}>
              Reward Summary
            </Typography>
            <Typography>Points: {summary.points}</Typography>
            <Typography>Discount per reward: {summary.reward_percent}%</Typography>
            <Typography color="text.secondary" mt={1}>
              Rewards are applied on eligible orders using your current loyalty status.
            </Typography>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>
            Apply Reward to Order
          </Typography>
          <TextField
            fullWidth
            label="Order ID"
            value={orderId}
            onChange={(event) => setOrderId(event.target.value)}
            placeholder="e.g. some-Uuid3"
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={applyReward} disabled={applyingReward}>
            {applyingReward ? <CircularProgress size={22} /> : 'Apply reward'}
          </Button>

          {applyResult && (
            <>
              <Divider sx={{ my: 2 }} />
              {applyResult.applied ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Reward applied successfully.
                </Alert>
              ) : (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Could not apply reward: {applyResult.reason ?? 'unknown_reason'}
                </Alert>
              )}

              {applyResult.applied && (
                <Box>
                  <Typography>Order: {applyResult.combined_order_id}</Typography>
                  <Typography>Original total: ${applyResult.order_total?.toFixed(2)}</Typography>
                  <Typography>
                    Discount ({applyResult.discount_percent}%): ${applyResult.discount_amount?.toFixed(2)}
                  </Typography>
                  <Typography fontWeight={600}>
                    New total: ${applyResult.discounted_total?.toFixed(2)}
                  </Typography>
                  <Button
                    variant="outlined"
                    sx={{ mt: 1 }}
                    onClick={() => goToCheckoutWithOrder(applyResult.combined_order_id)}
                  >
                    Go to checkout with this order
                  </Button>
                </Box>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoyaltyPage;
