import React, { useEffect, useState } from 'react';
import { Alert, Box, Button, CircularProgress, Stack, TextField, Typography } from '@mui/material';
import api from '../api';
import { useAuth } from '../auth/AuthContext';

interface MenuItem {
  food_item: string;
  price: number;
}

interface RestaurantResponse {
  id: number;
  menu_items: MenuItem[];
}

const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const [restaurantIdInput, setRestaurantIdInput] = useState('');
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingItemName, setSavingItemName] = useState<string | null>(null);
  const [nameEdits, setNameEdits] = useState<Record<string, string>>({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const assignedRestaurantId = user?.restaurant_manager_restaurant_id ?? null;
  const isManager = user?.user_type === 'restaurant_manager';

  useEffect(() => {
    if (assignedRestaurantId != null) {
      setRestaurantIdInput(String(assignedRestaurantId));
    }
  }, [assignedRestaurantId]);

  const loadMenu = async () => {
    const restaurantId = Number(restaurantIdInput);
    if (!restaurantId) {
      setError('Enter a valid restaurant ID first.');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const response = await api.get<RestaurantResponse>(`/restaurants/${restaurantId}`);
      setMenuItems(response.data.menu_items ?? []);
      setNameEdits({});
      if ((response.data.menu_items ?? []).length === 0) {
        setSuccess('No menu items found for this restaurant.');
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to load menu items.');
      setMenuItems([]);
    } finally {
      setLoading(false);
    }
  };

  const saveRename = async (oldName: string) => {
    const updatedName = (nameEdits[oldName] ?? '').trim();
    if (!updatedName) {
      setError('Menu item name cannot be empty.');
      return;
    }

    const restaurantId = Number(restaurantIdInput);
    setSavingItemName(oldName);
    setError('');
    setSuccess('');

    try {
      await api.put(
        `/restaurants/${restaurantId}/menu-items/${encodeURIComponent(oldName)}`,
        { food_item: updatedName },
      );

      setMenuItems((prev) => prev.map((item) => (
        item.food_item === oldName ? { ...item, food_item: updatedName } : item
      )));
      setNameEdits((prev) => {
        const next = { ...prev };
        delete next[oldName];
        return next;
      });
      setSuccess(`Updated "${oldName}" to "${updatedName}".`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to update menu item name.');
    } finally {
      setSavingItemName(null);
    }
  };

  if (!isManager) {
    return (
      <Box p={3}>
        <Alert severity="error">Only restaurant managers can access this page.</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" mb={1}>Admin</Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Rename menu items for your restaurant.
      </Typography>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={3}>
        <TextField
          label="Restaurant ID"
          value={restaurantIdInput}
          onChange={(event) => setRestaurantIdInput(event.target.value)}
          type="number"
          fullWidth
          disabled={assignedRestaurantId != null}
          helperText={assignedRestaurantId != null ? 'Locked to your assigned restaurant' : 'Enter a restaurant ID'}
        />
        <Button variant="contained" onClick={loadMenu} disabled={loading}>
          {loading ? 'Loading...' : 'Load menu'}
        </Button>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {loading ? (
        <CircularProgress />
      ) : (
        <Stack spacing={2}>
          {menuItems.map((item) => (
            <Stack key={item.food_item} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
              <TextField
                label="Current name"
                value={item.food_item}
                disabled
                fullWidth
              />
              <TextField
                label="New name"
                value={nameEdits[item.food_item] ?? ''}
                onChange={(event) => {
                  const value = event.target.value;
                  setNameEdits((prev) => ({ ...prev, [item.food_item]: value }));
                }}
                fullWidth
              />
              <Button
                variant="outlined"
                onClick={() => saveRename(item.food_item)}
                disabled={savingItemName === item.food_item}
              >
                {savingItemName === item.food_item ? 'Saving...' : 'Save'}
              </Button>
            </Stack>
          ))}
        </Stack>
      )}
    </Box>
  );
};

export default AdminPage;
