import React, { useEffect, useState } from 'react';
import { Typography, Box, CircularProgress, Card, CardContent, Chip } from '@mui/material';
import api from '../api';
import { useAuth } from '../auth/AuthContext';

interface Notification {
  id: number;
  order_id: string;
  message: string;
  notification_type: string;
  is_read: boolean;
}

const NotificationsPage: React.FC = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      setLoading(false);
      setError('You must be logged in to view notifications');
      return;
    }

    const fetchNotifications = async () => {
      try {
        const res = await api.get(`/notifications/history/${user.id}`);
        setNotifications(res.data.notifications || []);
      } catch {
        setError('Failed to load notifications');
      }
      setLoading(false);
    };

    fetchNotifications();
  }, [user]);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>Notifications</Typography>
      {notifications.length === 0 ? (
        <Typography>No notifications found</Typography>
      ) : (
        notifications.map((n) => (
          <Card key={n.id} sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="body1">{n.message}</Typography>
              <Typography variant="body2" color="text.secondary">Order: {n.order_id}</Typography>
              <Chip label={n.notification_type} size="small" sx={{ mt: 1, mr: 1 }} />
              <Chip label={n.is_read ? 'Read' : 'Unread'} size="small" color={n.is_read ? 'default' : 'primary'} sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};
export default NotificationsPage;