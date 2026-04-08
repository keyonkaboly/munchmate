import React, { useEffect, useMemo, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Typography, Box, CircularProgress, Divider, Card, CardContent, Button, TextField } from '@mui/material';
import api from '../api';
interface MenuItem {
  food_item: string;
  price: number;
  is_halal: boolean;
  is_vegetarian: boolean;
}
interface Restaurant {
  id: number;
  food_item: string;
  location: string;
  cuisine_type: string;
  is_halal: boolean;
  is_vegetarian: boolean;
  menu_items: MenuItem[];
}
const RestaurantDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [menuSearch, setMenuSearch] = useState('');

  useEffect(() => {
    const fetchRestaurant = async () => {
      try {
        const res = await api.get(`/restaurants/${id}`);
        setRestaurant(res.data);
      } catch (err: any) {
        setError('Failed to load restaurant');
      }
      setLoading(false);
    };
    fetchRestaurant();
  }, [id]);
  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!restaurant) return <Typography>Restaurant not found</Typography>;

  const filteredMenuItems = useMemo(() => {
    const query = menuSearch.trim().toLowerCase();
    if (!query) {
      return restaurant.menu_items;
    }

    return restaurant.menu_items.filter((item) => item.food_item.toLowerCase().includes(query));
  }, [menuSearch, restaurant.menu_items]);

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={1} mb={1}>
        <Typography variant="h4">Restaurant {restaurant.id}</Typography>
        <Button variant="contained" component={RouterLink} to={`/order?restaurantId=${restaurant.id}`}>
          Start order here
        </Button>
      </Box>
      <Typography variant="body1">Featured item: {restaurant.food_item}</Typography>
      <Typography variant="body1">Location: {restaurant.location}</Typography>
      <Typography variant="body1">Cuisine: {restaurant.cuisine_type}</Typography>
      <Typography variant="body1">Halal: {restaurant.is_halal ? 'Yes' : 'No'}</Typography>
      <Typography variant="body1">Vegetarian: {restaurant.is_vegetarian ? 'Yes' : 'No'}</Typography>
      <Divider sx={{ my: 3 }} />
      <Typography variant="h5" mb={2}>Menu</Typography>

      <TextField
        label="Search menu items"
        value={menuSearch}
        onChange={(event) => setMenuSearch(event.target.value)}
        placeholder="Try cake, pizza, salad..."
        fullWidth
        sx={{ mb: 2 }}
      />

      {filteredMenuItems.length === 0 ? (
        <Typography>No menu items available</Typography>
      ) : (
        filteredMenuItems.map((item, index) => (
          <Card key={index} sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="h6">{item.food_item}</Typography>
              <Typography variant="body2">Price: ${item.price?.toFixed(2)}</Typography>
              <Typography variant="body2">Halal: {item.is_halal ? 'Yes' : 'No'}</Typography>
              <Typography variant="body2">Vegetarian: {item.is_vegetarian ? 'Yes' : 'No'}</Typography>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};
export default RestaurantDetailPage;