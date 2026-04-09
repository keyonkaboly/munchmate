import React, { useEffect, useMemo, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Typography,
  Box,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Button,
  TextField,
  Checkbox,
  FormControlLabel,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Pagination,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
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

type SortBy = 'food_item' | 'price';
type SortOrder = 'asc' | 'desc';

const RestaurantDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [menuSearch, setMenuSearch] = useState('');
  const [onlyHalal, setOnlyHalal] = useState(false);
  const [onlyVegetarian, setOnlyVegetarian] = useState(false);
  const [sortBy, setSortBy] = useState<SortBy>('food_item');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);

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

  const filteredMenuItems = useMemo(() => {
    const menuItems = restaurant?.menu_items ?? [];
    const query = menuSearch.trim().toLowerCase();
    const filtered = menuItems.filter((item) => {
      const matchesQuery = !query || item.food_item.toLowerCase().includes(query);
      const matchesHalal = !onlyHalal || item.is_halal;
      const matchesVegetarian = !onlyVegetarian || item.is_vegetarian;
      return matchesQuery && matchesHalal && matchesVegetarian;
    });

    filtered.sort((left, right) => {
      if (sortBy === 'price') {
        return sortOrder === 'asc' ? left.price - right.price : right.price - left.price;
      }

      const compare = left.food_item.localeCompare(right.food_item);
      return sortOrder === 'asc' ? compare : -compare;
    });

    return filtered;
  }, [menuSearch, onlyHalal, onlyVegetarian, sortBy, sortOrder, restaurant]);

  const totalPages = Math.max(1, Math.ceil(filteredMenuItems.length / pageSize));

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const paginatedMenuItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredMenuItems.slice(start, start + pageSize);
  }, [filteredMenuItems, page, pageSize]);

  const handleSortByChange = (event: SelectChangeEvent<SortBy>) => {
    setSortBy(event.target.value as SortBy);
    setPage(1);
  };

  const handleSortOrderChange = (event: SelectChangeEvent<SortOrder>) => {
    setSortOrder(event.target.value as SortOrder);
    setPage(1);
  };

  const handlePageSizeChange = (event: SelectChangeEvent<number>) => {
    setPageSize(Number(event.target.value));
    setPage(1);
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!restaurant) return <Typography>Restaurant not found</Typography>;

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
        onChange={(event) => {
          setMenuSearch(event.target.value);
          setPage(1);
        }}
        placeholder="Try cake, pizza, salad..."
        fullWidth
        sx={{ mb: 2 }}
      />

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={2}>
        <FormControl fullWidth>
          <InputLabel id="menu-sort-by-label">Sort by</InputLabel>
          <Select
            labelId="menu-sort-by-label"
            label="Sort by"
            value={sortBy}
            onChange={handleSortByChange}
          >
            <MenuItem value="food_item">Name</MenuItem>
            <MenuItem value="price">Price</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="menu-sort-order-label">Sort order</InputLabel>
          <Select
            labelId="menu-sort-order-label"
            label="Sort order"
            value={sortOrder}
            onChange={handleSortOrderChange}
          >
            <MenuItem value="asc">Ascending</MenuItem>
            <MenuItem value="desc">Descending</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="menu-page-size-label">Per page</InputLabel>
          <Select
            labelId="menu-page-size-label"
            label="Per page"
            value={pageSize}
            onChange={handlePageSizeChange}
          >
            <MenuItem value={6}>6</MenuItem>
            <MenuItem value={12}>12</MenuItem>
            <MenuItem value={20}>20</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={2}>
        <FormControlLabel
          control={<Checkbox checked={onlyHalal} onChange={(e) => { setOnlyHalal(e.target.checked); setPage(1); }} />}
          label="Halal only"
        />
        <FormControlLabel
          control={<Checkbox checked={onlyVegetarian} onChange={(e) => { setOnlyVegetarian(e.target.checked); setPage(1); }} />}
          label="Vegetarian only"
        />
      </Stack>

      <Typography variant="body2" color="text.secondary" mb={2}>
        Showing {paginatedMenuItems.length} of {filteredMenuItems.length} menu items
      </Typography>

      {filteredMenuItems.length === 0 ? (
        <Typography>No menu items available</Typography>
      ) : (
        paginatedMenuItems.map((item, index) => (
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

      {totalPages > 1 && (
        <Stack direction="row" justifyContent="center" mt={3}>
          <Pagination page={page} count={totalPages} onChange={(_, value) => setPage(value)} color="primary" />
        </Stack>
      )}
    </Box>
  );
};
export default RestaurantDetailPage;