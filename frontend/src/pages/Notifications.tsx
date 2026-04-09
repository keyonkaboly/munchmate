import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Typography,
} from '@mui/material';
import api from '../api';
import { useAuth } from '../auth/AuthContext';
import { ACTIVE_ORDER_STORAGE_KEY } from '../customerSession';

interface Notification {
  id: number;
  order_id: string;
  message: string;
  notification_type: string;
  is_read: boolean;
}

interface GroupedOrder {
  order_id: string;
  restaurant_id: number;
  food_items: string[];
}

interface CustomerOrdersResponse {
  current_orders: GroupedOrder[];
  past_orders: GroupedOrder[];
}

function pickLatestOrderIdForReorder(
  notifications: Notification[],
  orders: CustomerOrdersResponse | null
): string | null {
  const sortedN = [...notifications].sort((a, b) => b.id - a.id);
  const fromN = sortedN.find((n) => n.order_id)?.order_id;
  if (fromN) return fromN;
  if (!orders) return null;
  const c = orders.current_orders || [];
  const p = orders.past_orders || [];
  if (c.length > 0) return c[c.length - 1].order_id;
  if (p.length > 0) return p[p.length - 1].order_id;
  return null;
}

const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [ordersSnapshot, setOrdersSnapshot] = useState<CustomerOrdersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [reorderBusy, setReorderBusy] = useState<string | null>(null);

  const fetchAll = useCallback(async (customerId: number) => {
    setError('');
    try {
      const [hist, ord] = await Promise.all([
        api.get<{ notifications: Notification[] }>(`/notifications/history/${customerId}`),
        api.get<CustomerOrdersResponse>(`/orders/customer/${customerId}`).catch(() => null),
      ]);
      setNotifications(hist.data.notifications || []);
      if (ord) setOrdersSnapshot(ord.data);
      else setOrdersSnapshot(null);
    } catch {
      setError('Failed to load notifications');
      setNotifications([]);
    }
  }, []);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      setError('You must be logged in to view notifications');
      return;
    }

    let cancelled = false;
    void (async () => {
      setLoading(true);
      await fetchAll(user.id);
      if (!cancelled) setLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [user, fetchAll]);

  const onRefresh = async () => {
    if (!user) return;
    setRefreshing(true);
    await fetchAll(user.id);
    setRefreshing(false);
  };

  const reorderForOrderId = async (orderId: string) => {
    if (!user) return;
    setReorderBusy(orderId);
    setError('');
    try {
      const res = await api.post<{ new_order_id: string }>(
        `/orders/${encodeURIComponent(orderId)}/reorder`,
        undefined,
        { params: { customer_id: String(user.id) } }
      );
      sessionStorage.setItem(ACTIVE_ORDER_STORAGE_KEY, res.data.new_order_id);
      navigate('/order');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Could not reorder.');
    }
    setReorderBusy(null);
  };

  const latestId = pickLatestOrderIdForReorder(notifications, ordersSnapshot);

  if (loading && !refreshing) {
    return (
      <Box p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return (
      <Box p={3}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>
        Notifications
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Logged in as customer #{user.id}. After a successful checkout payment, tap Refresh to see new alerts.
      </Typography>
      <Box mb={2} display="flex" gap={1} flexWrap="wrap" alignItems="center">
        <Button variant="outlined" size="small" onClick={() => void onRefresh()} disabled={refreshing}>
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </Button>
        {latestId && (
          <Button
            variant="contained"
            size="small"
            onClick={() => void reorderForOrderId(latestId)}
            disabled={reorderBusy !== null}
          >
            {reorderBusy === latestId ? <CircularProgress size={18} /> : 'Reorder last order'}
          </Button>
        )}
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      {notifications.length === 0 ? (
        <Typography>No notifications yet. Complete checkout and payment, then refresh.</Typography>
      ) : (
        notifications.map((n) => (
          <Card key={n.id} sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="body1">{n.message}</Typography>
              <Typography variant="body2" color="text.secondary">
                Order: {n.order_id}
              </Typography>
              <Chip label={n.notification_type} size="small" sx={{ mt: 1, mr: 1 }} />
              <Chip
                label={n.is_read ? 'Read' : 'Unread'}
                size="small"
                color={n.is_read ? 'default' : 'primary'}
                sx={{ mt: 1 }}
              />
              <Box mt={2}>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={reorderBusy !== null}
                  onClick={() => void reorderForOrderId(n.order_id)}
                >
                  {reorderBusy === n.order_id ? <CircularProgress size={18} /> : 'Order this again'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};

export default NotificationsPage;
