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

const CUSTOMER_STORAGE_KEY = 'munchmate_customer_id';

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
  const [customerId, setCustomerId] = useState<number>(readStoredCustomerId);
  const [orderId, setOrderId] = useState('');
  const [summary, setSummary] = useState<LoyaltySummary | null>(null);
  const [applyResult, setApplyResult] = useState<LoyaltyApplyResponse | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [applyingReward, setApplyingReward] = useState(false);
  const [error, setError] = useState('');

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
