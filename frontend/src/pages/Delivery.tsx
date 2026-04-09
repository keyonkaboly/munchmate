import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Alert, CircularProgress,
  Card, CardContent, Stack, Divider,
} from '@mui/material';
import api from '../api';

const PAID_ORDER_KEY = 'munchmate_paid_order_id';

interface DeliveryInfo {
  order_id: string;
  delivery_method: string;
  delivery_distance: number;
  delivery_time: string;
  delivery_time_actual: number;
  delivery_delay: number;
  route_taken: string;
  route_type: string;
  route_efficiency: number;
}

const DeliveryPage: React.FC = () => {
  const [delivery, setDelivery] = useState<DeliveryInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const orderId = sessionStorage.getItem(PAID_ORDER_KEY) ?? '';

  useEffect(() => {
    if (!orderId) {
      setError('No paid order found. Please complete checkout first.');
      setLoading(false);
      return;
    }
    const fetchDelivery = async () => {
      setLoading(true);
      try {
        const res = await api.get<DeliveryInfo>(`/orders/${orderId}`);
        setDelivery(res.data);

        // ~3 mins real time per km compressed to 3 seconds, delay adds 5s per minute

      } catch {
        setError('Could not load delivery info. Make sure your order has been paid.');
      }
      setLoading(false);
    };
    void fetchDelivery();
  }, [orderId]);

  

  
  if (loading) return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;

  return (
    <Box p={3} maxWidth={540} mx="auto">
      <Typography variant="h4" mb={2}>Delivery</Typography>

      {error && <Alert severity="warning">{error}</Alert>}


      {delivery && (
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" mb={2}>Delivery Info</Typography>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Order ID</Typography>
                <Typography variant="body2">{delivery.order_id}</Typography>
              </Stack>
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Delivery Method</Typography>
                <Typography variant="body2">{delivery.delivery_method}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Distance</Typography>
                <Typography variant="body2">{delivery.delivery_distance} km</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Estimated Delivery</Typography>
                <Typography variant="body2">~{Math.round(delivery.delivery_distance * 3 + delivery.delivery_delay)} mins</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Delay</Typography>
                <Typography variant="body2" color={delivery.delivery_delay > 0 ? 'error' : 'success.main'}>
                  {delivery.delivery_delay > 0 ? `+${delivery.delivery_delay} mins` : 'On time'}
                </Typography>
              </Stack>
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Route Taken</Typography>
                <Typography variant="body2">{delivery.route_taken}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Route Type</Typography>
                <Typography variant="body2">{delivery.route_type}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Route Efficiency</Typography>
                <Typography variant="body2">{delivery.route_efficiency}%</Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DeliveryPage;