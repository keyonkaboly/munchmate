import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Box, CircularProgress, Divider, Card, CardContent } from '@mui/material';
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
  return (
    <Box p={3}>
      <Typography variant="h4">{restaurant.food_item}</Typography>
      <Typography variant="body1">Location: {restaurant.location}</Typography>
      <Typography variant="body1">Cuisine: {restaurant.cuisine_type}</Typography>
      <Typography variant="body1">Halal: {restaurant.is_halal ? 'Yes' : 'No'}</Typography>
      <Typography variant="body1">Vegetarian: {restaurant.is_vegetarian ? 'Yes' : 'No'}</Typography>
      <Divider sx={{ my: 3 }} />
      <Typography variant="h5" mb={2}>Menu</Typography>
      {restaurant.menu_items.length === 0 ? (
        <Typography>No menu items available</Typography>
      ) : (
        restaurant.menu_items.map((item, index) => (
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