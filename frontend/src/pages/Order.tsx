import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Button, Select, MenuItem, FormControl, InputLabel,
  Alert, CircularProgress, List, ListItem, ListItemText,
  Card, CardContent, Divider, Chip, Stack,
} from '@mui/material';
import api from '../api';

const ACTIVE_ORDER_KEY = 'munchmate_active_order_id';

interface RestaurantListItem {
  id: number;
  food_item: string;
  location: string;
  cuisine_type: string;
}

interface RestaurantsResponse {
  items: RestaurantListItem[];
}

interface MenuItemRow {
  food_item: string;
  price: number;
  is_halal: boolean;
  is_vegetarian: boolean;
}

interface RestaurantDetail {
  id: number;
  food_item: string;
  menu_items: MenuItemRow[];
}

interface GroupedOrder {
  order_id: string;
  restaurant_id: number;
  customer_id: number;
  status: string;
  food_items: string[];
}

interface CustomerOrdersResponse {
  customer_id: string;
  current_orders: GroupedOrder[];
  past_orders: GroupedOrder[];
}

interface MeResponse {
  id: number;
}

interface CreateOrderResponse {
  combined_order_id?: string;
  order_id?: string;
}

const OrderPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const paramRestaurantId = searchParams.get('restaurantId');

  const [customerId, setCustomerId] = useState<number | null>(null);
  const [authError, setAuthError] = useState(false);
  const [restaurants, setRestaurants] = useState<RestaurantListItem[]>([]);
  const [restaurantId, setRestaurantId] = useState('');
  const [menuRestaurant, setMenuRestaurant] = useState<RestaurantDetail | null>(null);
  const [cart, setCart] = useState<string[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [menuLoading, setMenuLoading] = useState(false);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [customerOrders, setCustomerOrders] = useState<CustomerOrdersResponse | null>(null);

  const selectedIdNum = restaurantId ? parseInt(restaurantId, 10) : NaN;

  const cartCounts = useMemo(() => {
    const m: Record<string, number> = {};
    for (const name of cart) m[name] = (m[name] ?? 0) + 1;
    return m;
  }, [cart]);

  useEffect(() => {
    api.get<MeResponse>('/auth/me')
      .then((res) => setCustomerId(res.data.id))
      .catch(() => setAuthError(true));
  }, []);

  const loadRestaurants = useCallback(async () => {
    setListLoading(true);
    try {
      const res = await api.get<RestaurantsResponse>('/restaurants/');
      setRestaurants(res.data.items ?? []);
    } catch {
      setError('Failed to load restaurants');
    }
    setListLoading(false);
  }, []);

  const loadCustomerOrders = useCallback(async () => {
    if (customerId === null) return;
    setOrdersLoading(true);
    try {
      const res = await api.get<CustomerOrdersResponse>(`/orders/customer/${customerId}`);
      setCustomerOrders(res.data);
    } catch {
      setCustomerOrders(null);
    }
    setOrdersLoading(false);
  }, [customerId]);

  useEffect(() => { void loadRestaurants(); }, [loadRestaurants]);
  useEffect(() => { void loadCustomerOrders(); }, [loadCustomerOrders]);

  useEffect(() => {
    if (paramRestaurantId && restaurants.length > 0) {
      const exists = restaurants.some((r) => String(r.id) === paramRestaurantId);
      if (exists) setRestaurantId(paramRestaurantId);
    }
  }, [paramRestaurantId, restaurants]);

  useEffect(() => {
    if (!restaurantId) { setMenuRestaurant(null); return; }
    const fetchMenu = async () => {
      setMenuLoading(true);
      try {
        const res = await api.get<RestaurantDetail>(`/restaurants/${restaurantId}`);
        setMenuRestaurant(res.data);
      } catch {
        setMenuRestaurant(null);
        setError('Failed to load menu');
      }
      setMenuLoading(false);
    };
    void fetchMenu();
  }, [restaurantId]);

  const addToCart = (item: string) => setCart((c) => [...c, item]);

  const removeOneFromCart = (item: string) => {
    setCart((c) => {
      const idx = c.lastIndexOf(item);
      if (idx === -1) return c;
      return [...c.slice(0, idx), ...c.slice(idx + 1)];
    });
  };

  const getDetail = (err: unknown): string => {
    if (
      err instanceof Object && 'response' in err &&
      err.response instanceof Object && 'data' in err.response &&
      err.response.data instanceof Object && 'detail' in err.response.data
    ) {
      return (err.response.data as { detail: string }).detail ?? '';
    }
    return '';
  };

  const handlePlaceOrder = async () => {
    if (customerId === null || !Number.isFinite(selectedIdNum) || cart.length === 0) return;
    setError(''); setSuccess('');
    try {
      const res = await api.post<CreateOrderResponse>('/orders/create', {
        customer_id: customerId,
        restaurant_id: selectedIdNum,
        food_items: cart,
      });
      const oid = res.data.combined_order_id ?? res.data.order_id ?? '';
      sessionStorage.setItem(ACTIVE_ORDER_KEY, oid);
      setSuccess(`Order created! ID: ${oid} — click Checkout to pay.`);
      setCart([]);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const d = getDetail(err);
      setError(d || 'Could not create order');
    }
  };

  const handleSubmitOrder = async (orderId: string) => {
    setError(''); setSuccess('');
    try {
      await api.post(`/orders/${orderId}/submit`);
      setSuccess(`Order ${orderId} submitted.`);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const d = getDetail(err);
      setError(d || 'Submit failed');
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    setError(''); setSuccess('');
    try {
      await api.patch(`/orders/${orderId}/cancel`);
      setSuccess(`Order ${orderId} canceled.`);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const d = getDetail(err);
      setError(d || 'Cancel failed');
    }
  };

  const goToCheckout = (orderId: string) => {
    sessionStorage.setItem(ACTIVE_ORDER_KEY, orderId);
    navigate('/checkout');
  };

  if (authError) {
    return (
      <Box p={4} textAlign="center">
        <Alert severity="warning" sx={{ maxWidth: 480, mx: 'auto' }}>
          You need to be logged in to place orders. <a href="/auth">Log in here</a>.
        </Alert>
      </Box>
    );
  }

  if (customerId === null) {
    return <Box p={4} display="flex" justifyContent="center"><CircularProgress /></Box>;
  }

  return (
    <Box p={3}>
      <Typography variant="h4" mb={1}>Place an order</Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Logged in as customer #{customerId}. Pick a restaurant, add items, then click <strong>Checkout</strong> to pay.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      {listLoading ? <CircularProgress /> : (
        <FormControl fullWidth sx={{ maxWidth: 480, mb: 2 }}>
          <InputLabel id="rest-label">Restaurant</InputLabel>
          <Select
            labelId="rest-label"
            label="Restaurant"
            value={restaurantId}
            onChange={(e) => { setRestaurantId(e.target.value); setCart([]); }}
          >
            <MenuItem value=""><em>Select a restaurant</em></MenuItem>
            {restaurants.map((r) => (
              <MenuItem key={r.id} value={String(r.id)}>
                Restaurant {r.id} — {r.cuisine_type} ({r.location})
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {menuLoading && <CircularProgress sx={{ display: 'block', mb: 2 }} />}

      {menuRestaurant && !menuLoading && (
        <>
          <Typography variant="h6" mb={1}>Menu — Restaurant {menuRestaurant.id}</Typography>
          <List dense sx={{ mb: 2 }}>
            {menuRestaurant.menu_items.map((item) => (
              <ListItem
                key={item.food_item}
                secondaryAction={
                  <Button size="small" variant="outlined" onClick={() => addToCart(item.food_item)}>Add</Button>
                }
              >
                <ListItemText
                  primary={item.food_item}
                  secondary={`$${item.price?.toFixed(2) ?? '—'} · Halal: ${item.is_halal ? 'Yes' : 'No'} · Veg: ${item.is_vegetarian ? 'Yes' : 'No'}`}
                />
              </ListItem>
            ))}
          </List>
        </>
      )}

      <Divider sx={{ my: 2 }} />
      <Typography variant="h6" mb={1}>Cart</Typography>
      {cart.length === 0 ? (
        <Typography color="text.secondary">No items yet.</Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {Object.entries(cartCounts).map(([name, qty]) => (
            <Chip key={name} label={`${name} ×${qty}`} onDelete={() => removeOneFromCart(name)} sx={{ mr: 1, mb: 1 }} />
          ))}
          <Box><Button size="small" onClick={() => setCart([])}>Clear cart</Button></Box>
        </Box>
      )}

      <Button
        variant="contained"
        disabled={!Number.isFinite(selectedIdNum) || cart.length === 0}
        onClick={() => { void handlePlaceOrder(); }}
      >
        Create order
      </Button>

      <Divider sx={{ my: 3 }} />
      <Stack direction="row" alignItems="center" gap={2} mb={2}>
        <Typography variant="h5">Your orders</Typography>
        <Button size="small" onClick={() => { void loadCustomerOrders(); }} disabled={ordersLoading}>Refresh</Button>
      </Stack>

      {ordersLoading ? <CircularProgress size={24} /> : customerOrders ? (
        <>
          <Typography variant="subtitle1" fontWeight="bold">In progress</Typography>
          {customerOrders.current_orders.length === 0 ? (
            <Typography color="text.secondary">None</Typography>
          ) : customerOrders.current_orders.map((o) => (
            <Card key={o.order_id} sx={{ mb: 1, mt: 1 }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">{o.order_id}</Typography>
                <Typography variant="body1">Restaurant #{o.restaurant_id} · <strong>{o.status}</strong></Typography>
                <Typography variant="body2">{o.food_items.join(', ')}</Typography>
                <Stack direction="row" gap={1} mt={1} flexWrap="wrap">
                  {o.status === 'Created' && (
                    <>
                      <Button size="small" variant="contained" onClick={() => { void handleSubmitOrder(o.order_id); }}>Submit</Button>
                      <Button size="small" variant="outlined" onClick={() => goToCheckout(o.order_id)}>Checkout</Button>
                      <Button size="small" color="warning" onClick={() => { void handleCancelOrder(o.order_id); }}>Cancel</Button>
                    </>
                  )}
                  {o.status === 'Submitted' && (
                    <Button size="small" variant="outlined" onClick={() => goToCheckout(o.order_id)}>Checkout</Button>
                  )}
                </Stack>
              </CardContent>
            </Card>
          ))}

          <Typography variant="subtitle1" fontWeight="bold" mt={2}>Past orders</Typography>
          {customerOrders.past_orders.length === 0 ? (
            <Typography color="text.secondary">None</Typography>
          ) : customerOrders.past_orders.map((o) => (
            <Card key={o.order_id} sx={{ mb: 1, mt: 1 }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">{o.order_id}</Typography>
                <Typography variant="body2" color="text.secondary">{o.status}</Typography>
                <Typography variant="body2">{o.food_items.join(', ')}</Typography>
              </CardContent>
            </Card>
          ))}
        </>
      ) : (
        <Typography color="text.secondary">Could not load orders.</Typography>
      )}
    </Box>
  );
};

export default OrderPage;