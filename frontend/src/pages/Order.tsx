import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Divider,
  Chip,
} from '@mui/material';
import api from '../api';

const CUSTOMER_STORAGE_KEY = 'munchmate_customer_id';
const ACTIVE_ORDER_STORAGE_KEY = 'munchmate_active_order_id';

interface RestaurantListItem {
  id: number;
  food_item: string;
  location: string;
  cuisine_type: string;
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

function readStoredCustomerId(): number {
  const raw = sessionStorage.getItem(CUSTOMER_STORAGE_KEY);
  if (raw == null || raw === '') return 1;
  const n = parseInt(raw, 10);
  return Number.isFinite(n) ? n : 1;
}

const OrderPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const paramRestaurantId = searchParams.get('restaurantId');

  const [customerId, setCustomerId] = useState(readStoredCustomerId);
  const [restaurants, setRestaurants] = useState<RestaurantListItem[]>([]);
  const [restaurantId, setRestaurantId] = useState<string>('');
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
    for (const name of cart) {
      m[name] = (m[name] || 0) + 1;
    }
    return m;
  }, [cart]);

  const loadRestaurants = useCallback(async () => {
    setListLoading(true);
    setError('');
    try {
      const res = await api.get('/restaurants/');
      setRestaurants(res.data.items || []);
    } catch {
      setError('Failed to load restaurants');
    }
    setListLoading(false);
  }, []);

  const loadCustomerOrders = useCallback(async () => {
    setOrdersLoading(true);
    try {
      const res = await api.get<CustomerOrdersResponse>(`/orders/customer/${customerId}`);
      setCustomerOrders(res.data);
    } catch {
      setCustomerOrders(null);
    }
    setOrdersLoading(false);
  }, [customerId]);

  useEffect(() => {
    loadRestaurants();
  }, [loadRestaurants]);

  useEffect(() => {
    sessionStorage.setItem(CUSTOMER_STORAGE_KEY, String(customerId));
  }, [customerId]);

  useEffect(() => {
    loadCustomerOrders();
  }, [loadCustomerOrders]);

  useEffect(() => {
    if (paramRestaurantId && restaurants.length > 0) {
      const exists = restaurants.some((r) => String(r.id) === paramRestaurantId);
      if (exists) setRestaurantId(paramRestaurantId);
    }
  }, [paramRestaurantId, restaurants]);

  useEffect(() => {
    if (!restaurantId) {
      setMenuRestaurant(null);
      return;
    }
    const fetchMenu = async () => {
      setMenuLoading(true);
      setError('');
      try {
        const res = await api.get<RestaurantDetail>(`/restaurants/${restaurantId}`);
        setMenuRestaurant(res.data);
      } catch {
        setMenuRestaurant(null);
        setError('Failed to load menu');
      }
      setMenuLoading(false);
    };
    fetchMenu();
  }, [restaurantId]);

  const addToCart = (foodItem: string) => {
    setCart((c) => [...c, foodItem]);
    setSuccess('');
  };

  const removeOneFromCart = (foodItem: string) => {
    setCart((c) => {
      const idx = c.lastIndexOf(foodItem);
      if (idx === -1) return c;
      return [...c.slice(0, idx), ...c.slice(idx + 1)];
    });
  };

  const handlePlaceOrder = async () => {
    if (!Number.isFinite(selectedIdNum) || cart.length === 0) return;
    setError('');
    setSuccess('');
    try {
      const res = await api.post('/orders/create', {
        customer_id: customerId,
        restaurant_id: selectedIdNum,
        food_items: cart,
      });
      const oid = res.data.combined_order_id || res.data.order_id;
      sessionStorage.setItem(ACTIVE_ORDER_STORAGE_KEY, oid);
      setSuccess(`Order created. ID: ${oid}`);
      setCart([]);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Could not create order');
    }
  };

  const handleSubmitOrder = async (orderId: string) => {
    setError('');
    setSuccess('');
    try {
      await api.post(`/orders/${orderId}/submit`);
      setSuccess(`Order ${orderId} submitted.`);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Submit failed');
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    setError('');
    setSuccess('');
    try {
      await api.patch(`/orders/${orderId}/cancel`);
      setSuccess(`Order ${orderId} canceled.`);
      await loadCustomerOrders();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Cancel failed');
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>
        Place an order
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Choose a restaurant, add menu items, then create the order. Use the same customer ID as elsewhere (e.g. notifications). After creating an order, continue to Checkout to calculate totals and pay.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <TextField
        label="Customer ID"
        type="number"
        size="small"
        value={customerId}
        onChange={(e) => {
          const n = parseInt(e.target.value, 10);
          setCustomerId(Number.isFinite(n) && n > 0 ? n : 1);
        }}
        sx={{ mb: 2, maxWidth: 200 }}
        helperText="Must match the user you use for notifications/history"
      />

      {listLoading ? (
        <CircularProgress />
      ) : (
        <FormControl fullWidth sx={{ maxWidth: 480, mb: 2 }}>
          <InputLabel id="restaurant-select-label">Restaurant</InputLabel>
          <Select
            labelId="restaurant-select-label"
            label="Restaurant"
            value={restaurantId}
            onChange={(e) => {
              setRestaurantId(e.target.value);
              setCart([]);
            }}
          >
            <MenuItem value="">
              <em>Select a restaurant</em>
            </MenuItem>
            {restaurants.map((r) => (
              <MenuItem key={r.id} value={String(r.id)}>
                Restaurant {r.id}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {menuLoading && <CircularProgress sx={{ display: 'block', mb: 2 }} />}

      {menuRestaurant && !menuLoading && (
        <>
          <Typography variant="h6" mb={1}>
            Menu — Restaurant {menuRestaurant.id}
          </Typography>
          <List dense sx={{ mb: 2 }}>
            {menuRestaurant.menu_items.map((item) => (
              <ListItem
                key={item.food_item}
                secondaryAction={
                  <Button size="small" variant="outlined" onClick={() => addToCart(item.food_item)}>
                    Add
                  </Button>
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
      <Typography variant="h6" mb={1}>
        Cart
      </Typography>
      {cart.length === 0 ? (
        <Typography color="text.secondary">No items yet.</Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {Object.entries(cartCounts).map(([name, qty]) => (
            <Chip
              key={name}
              label={`${name} × ${qty}`}
              onDelete={() => removeOneFromCart(name)}
              sx={{ mr: 1, mb: 1 }}
            />
          ))}
          <Box>
            <Button size="small" onClick={() => setCart([])}>
              Clear cart
            </Button>
          </Box>
        </Box>
      )}

      <Button
        variant="contained"
        disabled={!Number.isFinite(selectedIdNum) || cart.length === 0}
        onClick={handlePlaceOrder}
      >
        Create order
      </Button>

      <Divider sx={{ my: 3 }} />
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <Typography variant="h5">Your orders</Typography>
        <Button size="small" onClick={loadCustomerOrders} disabled={ordersLoading}>
          Refresh
        </Button>
      </Box>
      {ordersLoading ? (
        <CircularProgress size={24} />
      ) : customerOrders ? (
        <>
          <Typography variant="subtitle1" fontWeight="bold" mt={2}>
            In progress
          </Typography>
          {customerOrders.current_orders.length === 0 ? (
            <Typography color="text.secondary">None</Typography>
          ) : (
            customerOrders.current_orders.map((o) => (
              <Card key={o.order_id} sx={{ mb: 1, mt: 1 }}>
                <CardContent>
                  <Typography variant="subtitle1">{o.order_id}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Restaurant #{o.restaurant_id} · {o.status}
                  </Typography>
                  <Typography variant="body2">{o.food_items.join(', ')}</Typography>
                  {o.status === 'Created' && (
                    <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                      <Button size="small" variant="contained" onClick={() => handleSubmitOrder(o.order_id)}>
                        Submit order
                      </Button>
                      <Button size="small" color="warning" onClick={() => handleCancelOrder(o.order_id)}>
                        Cancel
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))
          )}
          <Typography variant="subtitle1" fontWeight="bold" mt={2}>
            Past
          </Typography>
          {customerOrders.past_orders.length === 0 ? (
            <Typography color="text.secondary">None</Typography>
          ) : (
            customerOrders.past_orders.map((o) => (
              <Card key={o.order_id} sx={{ mb: 1, mt: 1 }}>
                <CardContent>
                  <Typography variant="subtitle1">{o.order_id}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {o.status}
                  </Typography>
                  <Typography variant="body2">{o.food_items.join(', ')}</Typography>
                </CardContent>
              </Card>
            ))
          )}
        </>
      ) : (
        <Typography color="text.secondary">Could not load orders.</Typography>
      )}
    </Box>
  );
};

export default OrderPage;
