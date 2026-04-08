import React, { useEffect, useState, useCallback } from 'react';
import {
  Typography,
  Box,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Button,
  Divider,
  Stack,
  Alert,
  Snackbar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../api';

interface NotificationItem {
  id: number;
  order_id: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  restaurant_id?: number | null;
  food_items?: string[];
}

interface NotificationsResponse {
  notifications: NotificationItem[];
}

interface MeResponse {
  id: number;
}

interface ReorderResponse {
  new_order_id: string;
}

const TYPE_LABEL: Record<string, string> = {
  order_confirmed: 'Order Confirmed',
  order_cancelled: 'Order Cancelled',
  delivery_status: 'Delivery Update',
  incoming_order: 'Incoming Order',
  reorder_suggestion: 'Reorder Suggestion',
};

const TYPE_COLOR: Record<string, 'default' | 'primary' | 'success' | 'error' | 'warning' | 'info'> = {
  order_confirmed: 'success',
  order_cancelled: 'error',
  delivery_status: 'info',
  incoming_order: 'warning',
  reorder_suggestion: 'primary',
};

const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [customerId, setCustomerId] = useState<number | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [fetchError, setFetchError] = useState('');
  const [snack, setSnack] = useState('');
  const [reordering, setReordering] = useState<number | null>(null);

  useEffect(() => {
    api.get<MeResponse>('/auth/me')
      .then((res) => setCustomerId(res.data.id))
      .catch(() => {
        setAuthError(true);
        setLoading(false);
      });
  }, []);

  const fetchNotifications = useCallback(async () => {
    if (customerId === null) return;
    setLoading(true);
    setFetchError('');
    try {
      const res = await api.get<NotificationsResponse>(`/notifications/history/${customerId}`);
      setNotifications(res.data.notifications ?? []);
    } catch {
      setFetchError('Failed to load notifications. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, [customerId]);

  useEffect(() => {
    void fetchNotifications();
  }, [fetchNotifications]);

  const markAsRead = async (id: number) => {
    try {
      await api.patch(`/notifications/${id}/read`);
    } catch {
      // best-effort
    }
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  };

  const markAllRead = async () => {
    const unread = notifications.filter((n) => !n.is_read);
    await Promise.allSettled(unread.map((n) => api.patch(`/notifications/${n.id}/read`)));
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const handleReorder = async (n: NotificationItem) => {
    if (customerId === null || !n.restaurant_id) return;
    setReordering(n.id);
    try {
      const res = await api.post<ReorderResponse>(
        `/orders/${n.order_id}/reorder`,
        null,
        { params: { customer_id: customerId } }
      );
      const newOrderId = res.data.new_order_id;
      await api.patch(`/notifications/${n.id}/read`).catch(() => undefined);
      setNotifications((prev) => prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
      setSnack(`Reorder created! ID: ${newOrderId} — go to Checkout to pay.`);
      navigate(`/order?restaurantId=${n.restaurant_id}`);
    } catch (err: unknown) {
      const detail =
        err instanceof Object && 'response' in err &&
        err.response instanceof Object && 'data' in err.response &&
        err.response.data instanceof Object && 'detail' in err.response.data
          ? (err.response.data as { detail: string }).detail
          : '';
      setSnack(typeof detail === 'string' && detail ? detail : 'Reorder failed. Please try again.');
    } finally {
      setReordering(null);
    }
  };

  if (authError) {
    return (
      <Box p={4} textAlign="center">
        <Alert severity="warning" sx={{ maxWidth: 480, mx: 'auto' }}>
          You need to be logged in to view notifications. <a href="/auth">Log in here</a>.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  if (fetchError) {
    return (
      <Box p={4}>
        <Alert severity="error" action={<Button onClick={() => { void fetchNotifications(); }}>Retry</Button>}>
          {fetchError}
        </Alert>
      </Box>
    );
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <Box p={3} maxWidth={720} mx="auto">
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
        <Stack direction="row" alignItems="center" gap={1}>
          <Typography variant="h4">Notifications</Typography>
          {unreadCount > 0 && <Chip label={`${unreadCount} unread`} color="primary" size="small" />}
        </Stack>
        <Stack direction="row" gap={1}>
          {unreadCount > 0 && (
            <Button variant="outlined" size="small" onClick={() => { void markAllRead(); }}>
              Mark all read
            </Button>
          )}
          <Button variant="outlined" size="small" onClick={() => { void fetchNotifications(); }}>
            Refresh
          </Button>
        </Stack>
      </Stack>

      <Divider sx={{ mb: 2 }} />

      {notifications.length === 0 ? (
        <Box textAlign="center" py={8}>
          <Typography variant="h2">🔔</Typography>
          <Typography color="text.secondary">No notifications yet.</Typography>
        </Box>
      ) : (
        notifications.map((n) => {
          const isReorder = n.notification_type === 'reorder_suggestion';
          return (
            <Card
              key={n.id}
              sx={{
                mb: 1.5,
                borderLeft: '4px solid',
                borderLeftColor: n.is_read ? 'divider' : 'primary.main',
                opacity: n.is_read ? 0.72 : 1,
              }}
            >
              <CardContent>
                <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={1}>
                  <Box flex={1}>
                    <Typography variant="body1" fontWeight={n.is_read ? 400 : 600} gutterBottom>
                      {n.message}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      Order: {n.order_id}
                    </Typography>
                    {isReorder && n.food_items && n.food_items.length > 0 && (
                      <Typography variant="body2" color="text.secondary" mb={1}>
                        Items: {n.food_items.join(', ')}
                      </Typography>
                    )}
                    <Stack direction="row" gap={0.5} flexWrap="wrap">
                      <Chip
                        label={TYPE_LABEL[n.notification_type] ?? n.notification_type}
                        color={TYPE_COLOR[n.notification_type] ?? 'default'}
                        size="small"
                      />
                      <Chip
                        label={n.is_read ? 'Read' : 'Unread'}
                        size="small"
                        variant={n.is_read ? 'outlined' : 'filled'}
                        color={n.is_read ? 'default' : 'primary'}
                      />
                    </Stack>
                  </Box>
                  <Stack direction="column" gap={0.5} alignItems="flex-end" flexShrink={0}>
                    {isReorder && (
                      <Button
                        variant="contained"
                        size="small"
                        disabled={reordering === n.id}
                        onClick={() => { void handleReorder(n); }}
                      >
                        {reordering === n.id ? 'Ordering…' : '🔁 Reorder'}
                      </Button>
                    )}
                    {!n.is_read && (
                      <Button size="small" onClick={() => { void markAsRead(n.id); }}>
                        Mark read
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          );
        })
      )}

      <Snackbar
        open={Boolean(snack)}
        autoHideDuration={6000}
        onClose={() => setSnack('')}
        message={snack}
      />
    </Box>
  );
};

export default NotificationsPage;