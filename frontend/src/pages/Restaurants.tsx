import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Pagination,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
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

type SortBy = 'id' | 'location' | 'cuisine_type';
type SortOrder = 'asc' | 'desc';

const CUISINE_OPTIONS = [
  'American',
  'Asian',
  'Desserts & Drinks',
  'Italian',
  'Mediterranean',
  'Mexican',
  'Other',
];

const PAGE_FETCH_SIZE = 20;
const MIN_RESTAURANT_ID = 1;
const MAX_RESTAURANT_ID = 100;

const restaurantDisplayName = (restaurantId: number): string => `Restaurant ${restaurantId}`;
const restaurantMisspelledDisplayName = (restaurantId: number): string => `Resturant ${restaurantId}`;

const RestaurantsPage: React.FC = () => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchText, setSearchText] = useState('');
  const [onlyHalal, setOnlyHalal] = useState(false);
  const [onlyVegetarian, setOnlyVegetarian] = useState(false);
  const [cuisineType, setCuisineType] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('id');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRestaurants = async () => {
      setLoading(true);
      setError('');

      try {
        const allItems: Restaurant[] = [];
        let nextPage = 1;
        let totalPages = 1;

        while (nextPage <= totalPages) {
          const params: Record<string, string | number | boolean> = {
            page: nextPage,
            page_size: PAGE_FETCH_SIZE,
          };

          if (onlyHalal) {
            params.is_halal = true;
          }

          if (onlyVegetarian) {
            params.is_vegetarian = true;
          }

          if (cuisineType) {
            params.cuisine_type = cuisineType;
          }

          const res = await api.get('/restaurants/', { params });

          if (res.data?.message === 'No restaurants found') {
            break;
          }

          const items = (res.data?.items || []) as Restaurant[];
          allItems.push(...items);
          totalPages = res.data?.total_pages || 1;
          nextPage += 1;
        }

        const uniqueById = new Map<number, Restaurant>();
        for (const item of allItems) {
          if (!uniqueById.has(item.id)) {
            uniqueById.set(item.id, item);
          }
        }

        const normalized = Array.from(uniqueById.values()).filter(
          (restaurant) => restaurant.id >= MIN_RESTAURANT_ID && restaurant.id <= MAX_RESTAURANT_ID,
        );

        setRestaurants(normalized);
      } catch (err: any) {
        setError('Failed to load restaurants');
      }

      setLoading(false);
    };

    fetchRestaurants();
  }, [onlyHalal, onlyVegetarian, cuisineType]);

  const filteredAndSortedRestaurants = useMemo(() => {
    const query = searchText.trim().toLowerCase();
    const filtered = restaurants.filter((restaurant) => {
      if (!query) {
        return true;
      }

      const displayName = restaurantDisplayName(restaurant.id).toLowerCase();
      const misspelledDisplayName = restaurantMisspelledDisplayName(restaurant.id).toLowerCase();
      const idAsText = String(restaurant.id);

      return (
        displayName.includes(query) ||
        misspelledDisplayName.includes(query) ||
        idAsText.includes(query) ||
        restaurant.location.toLowerCase().includes(query) ||
        restaurant.cuisine_type.toLowerCase().includes(query)
      );
    });

    filtered.sort((left, right) => {
      const leftValue = left[sortBy];
      const rightValue = right[sortBy];

      if (typeof leftValue === 'number' && typeof rightValue === 'number') {
        return sortOrder === 'asc' ? leftValue - rightValue : rightValue - leftValue;
      }

      const compareValue = String(leftValue).localeCompare(String(rightValue));
      return sortOrder === 'asc' ? compareValue : -compareValue;
    });

    return filtered;
  }, [restaurants, searchText, sortBy, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(filteredAndSortedRestaurants.length / pageSize));

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const paginatedRestaurants = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredAndSortedRestaurants.slice(start, start + pageSize);
  }, [filteredAndSortedRestaurants, page, pageSize]);

  const handleSortByChange = (event: SelectChangeEvent<SortBy>) => {
    setSortBy(event.target.value as SortBy);
    setPage(1);
  };

  const handleSortOrderChange = (event: SelectChangeEvent<SortOrder>) => {
    setSortOrder(event.target.value as SortOrder);
    setPage(1);
  };

  const handleCuisineChange = (event: SelectChangeEvent<string>) => {
    setCuisineType(event.target.value);
    setPage(1);
  };

  const handlePageSizeChange = (event: SelectChangeEvent<number>) => {
    setPageSize(Number(event.target.value));
    setPage(1);
  };

  return (
    <Box p={2}>
      <Typography variant="h4" mb={2}>Restaurants</Typography>

      <Stack spacing={2} mb={3}>
        <TextField
          label="Search restaurants"
          value={searchText}
          onChange={(event) => {
            setSearchText(event.target.value);
            setPage(1);
          }}
          placeholder="Search by Restaurant 1, Resturant 1, ID, location, or cuisine"
          fullWidth
        />

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <FormControl fullWidth>
            <InputLabel id="cuisine-label">Cuisine</InputLabel>
            <Select
              labelId="cuisine-label"
              value={cuisineType}
              label="Cuisine"
              onChange={handleCuisineChange}
            >
              <MenuItem value="">All cuisines</MenuItem>
              {CUISINE_OPTIONS.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="sort-by-label">Sort by</InputLabel>
            <Select
              labelId="sort-by-label"
              value={sortBy}
              label="Sort by"
              onChange={handleSortByChange}
            >
              <MenuItem value="id">Restaurant ID</MenuItem>
              <MenuItem value="location">Location</MenuItem>
              <MenuItem value="cuisine_type">Cuisine</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="sort-order-label">Sort order</InputLabel>
            <Select
              labelId="sort-order-label"
              value={sortOrder}
              label="Sort order"
              onChange={handleSortOrderChange}
            >
              <MenuItem value="asc">Ascending</MenuItem>
              <MenuItem value="desc">Descending</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="page-size-label">Per page</InputLabel>
            <Select
              labelId="page-size-label"
              value={pageSize}
              label="Per page"
              onChange={handlePageSizeChange}
            >
              <MenuItem value={6}>6</MenuItem>
              <MenuItem value={12}>12</MenuItem>
              <MenuItem value={20}>20</MenuItem>
            </Select>
          </FormControl>
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <FormControlLabel
            control={
              <Checkbox
                checked={onlyHalal}
                onChange={(event) => {
                  setOnlyHalal(event.target.checked);
                  setPage(1);
                }}
              />
            }
            label="Halal only"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={onlyVegetarian}
                onChange={(event) => {
                  setOnlyVegetarian(event.target.checked);
                  setPage(1);
                }}
              />
            }
            label="Vegetarian only"
          />
        </Stack>

        <Typography variant="body2" color="text.secondary">
          Showing {paginatedRestaurants.length} of {filteredAndSortedRestaurants.length} results
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Default list includes one instance each for Restaurant IDs 1–100.
        </Typography>
      </Stack>

      {loading ? <CircularProgress /> : error ? <Typography color="error">{error}</Typography> : (
        <Grid container spacing={2}>
          {paginatedRestaurants.map(r => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={r.id}>
              <Card onClick={() => navigate(`/restaurants/${r.id}`)} sx={{ cursor: 'pointer' }}>
                <CardContent>
                  <Typography variant="h6">{restaurantDisplayName(r.id)}</Typography>
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

      {!loading && !error && totalPages > 1 && (
        <Stack direction="row" justifyContent="center" mt={3}>
          <Pagination
            page={page}
            count={totalPages}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Stack>
      )}
    </Box>
  );
};

export default RestaurantsPage;
