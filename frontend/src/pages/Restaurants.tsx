import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, CircularProgress, Box, TextField, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../api';

interface Restaurant {
  id: number;
  food_item: string;
  location: string;
  cuisine_type: string;
  is_halal: boolean;
  is_vegetarian: boolean;
}

const RestaurantsPage: React.FC = () => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRestaurants = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get('/restaurants/');
        setRestaurants(res.data.items || []);
      } catch (err: any) {
        setError('Failed to load restaurants');
      }
      setLoading(false);
    };
    fetchRestaurants();
  }, []);

  return (
    <Box p={2}>
      <Typography variant="h4" mb={2}>Restaurants</Typography>
      {loading ? <CircularProgress /> : error ? <Typography color="error">{error}</Typography> : (
        <Grid container spacing={2}>
          {restaurants.map(r => (
            <Grid item xs={12} sm={6} md={4} key={r.id}>
              <Card onClick={() => navigate(`/restaurants/${r.id}`)} sx={{ cursor: 'pointer' }}>
                <CardContent>
                  <Typography variant="h6">{r.food_item}</Typography>
                  <Typography variant="body2">Location: {r.location}</Typography>
                  <Typography variant="body2">Cuisine: {r.cuisine_type}</Typography>
                  <Typography variant="body2">Halal: {r.is_halal ? 'Yes' : 'No'}</Typography>
                  <Typography variant="body2">Vegetarian: {r.is_vegetarian ? 'Yes' : 'No'}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default RestaurantsPage;
