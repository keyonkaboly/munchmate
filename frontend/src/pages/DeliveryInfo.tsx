import React, { useEffect, useMemo, useState } from 'react';
import {
	Alert,
	Box,
	Card,
	CardContent,
	CircularProgress,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	Stack,
	Typography,
} from '@mui/material';
import { useAuth } from '../auth/AuthContext';
import api from '../api';

interface GroupedOrder {
	order_id: string;
	status: string;
	restaurant_id: number;
	food_items: string[];
}

interface CustomerOrdersResponse {
	customer_id: string;
	current_orders: GroupedOrder[];
	past_orders: GroupedOrder[];
}

interface DeliveryOrderResponse {
	order_id: string;
	delivery_method?: string | null;
	delivery_distance?: number | null;
	delivery_time?: string | null;
	delivery_time_actual?: number | null;
	delivery_delay?: number | null;
	route_taken?: string | null;
	route_type?: string | null;
	route_efficiency?: number | null;
}

const DeliveryInfoPage: React.FC = () => {
	const { user } = useAuth();
	const [orders, setOrders] = useState<GroupedOrder[]>([]);
	const [selectedOrderId, setSelectedOrderId] = useState('');
	const [deliveryInfo, setDeliveryInfo] = useState<DeliveryOrderResponse | null>(null);
	const [loadingOrders, setLoadingOrders] = useState(false);
	const [loadingDetails, setLoadingDetails] = useState(false);
	const [error, setError] = useState('');

	const orderMap = useMemo(() => {
		const map = new Map<string, GroupedOrder>();
		for (const order of orders) {
			map.set(order.order_id, order);
		}
		return map;
	}, [orders]);

	const selectedOrder = selectedOrderId ? orderMap.get(selectedOrderId) : undefined;

	useEffect(() => {
		const loadOrders = async () => {
			if (!user?.id) return;
			setLoadingOrders(true);
			setError('');
			try {
				const res = await api.get<CustomerOrdersResponse>(`/orders/customer/${user.id}`);
				const merged = [...res.data.current_orders, ...res.data.past_orders];
				setOrders(merged);

				if (merged.length > 0) {
					setSelectedOrderId((prev) => (prev && merged.some((order) => order.order_id === prev) ? prev : merged[0].order_id));
				}
			} catch {
				setError('Failed to load your orders for delivery details.');
			} finally {
				setLoadingOrders(false);
			}
		};

		void loadOrders();
	}, [user?.id]);

	useEffect(() => {
		const loadDeliveryDetails = async () => {
			if (!selectedOrderId) {
				setDeliveryInfo(null);
				return;
			}

			setLoadingDetails(true);
			setError('');
			try {
				const res = await api.get<DeliveryOrderResponse>(`/orders/${selectedOrderId}`);
				setDeliveryInfo(res.data);
			} catch {
				setDeliveryInfo(null);
				setError('Failed to load delivery details for selected order.');
			} finally {
				setLoadingDetails(false);
			}
		};

		void loadDeliveryDetails();
	}, [selectedOrderId]);

	return (
		<Box p={3} maxWidth={760} mx="auto">
			<Typography variant="h4" mb={1}>Delivery</Typography>
			<Typography variant="body2" color="text.secondary" mb={2}>
				Select an order to view its delivery information.
			</Typography>

			{error && (
				<Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
					{error}
				</Alert>
			)}

			<Card variant="outlined">
				<CardContent>
					<Stack spacing={2}>
						<FormControl fullWidth>
							<InputLabel id="delivery-order-label">Order</InputLabel>
							<Select
								labelId="delivery-order-label"
								label="Order"
								value={selectedOrderId}
								onChange={(event) => setSelectedOrderId(event.target.value)}
								disabled={loadingOrders || orders.length === 0}
							>
								{orders.map((order) => (
									<MenuItem key={order.order_id} value={order.order_id}>
										{order.order_id}
									</MenuItem>
								))}
							</Select>
						</FormControl>

						{(loadingOrders || loadingDetails) && (
							<Box display="flex" justifyContent="center" py={1}>
								<CircularProgress size={26} />
							</Box>
						)}

						{!loadingOrders && orders.length === 0 && (
							<Typography color="text.secondary">No orders found yet.</Typography>
						)}

						{!loadingDetails && deliveryInfo && (
							<Stack spacing={0.8}>
								<Typography variant="subtitle1" fontWeight="bold">Order #{deliveryInfo.order_id}</Typography>
								<Typography variant="body2">Status: {selectedOrder?.status ?? 'Unknown'}</Typography>
								<Typography variant="body2">Restaurant: {selectedOrder ? `#${selectedOrder.restaurant_id}` : 'Unknown'}</Typography>
								<Typography variant="body2">Items: {selectedOrder?.food_items?.join(', ') || 'Unavailable'}</Typography>
								<Typography variant="body2">Delivery method: {deliveryInfo.delivery_method ?? 'Pending'}</Typography>
								<Typography variant="body2">Delivery distance: {deliveryInfo.delivery_distance != null ? `${deliveryInfo.delivery_distance} km` : 'Pending'}</Typography>
								<Typography variant="body2">Delivery delay: {deliveryInfo.delivery_delay != null ? `${deliveryInfo.delivery_delay} min` : 'Pending'}</Typography>
								<Typography variant="body2">Route taken: {deliveryInfo.route_taken ?? 'Pending'}</Typography>
								<Typography variant="body2">Route type: {deliveryInfo.route_type ?? 'Pending'}</Typography>
								<Typography variant="body2">Route efficiency: {deliveryInfo.route_efficiency != null ? deliveryInfo.route_efficiency : 'Pending'}</Typography>
								<Typography variant="body2">Estimated time: {deliveryInfo.delivery_time ?? 'Pending'}</Typography>
								<Typography variant="body2">Actual time: {deliveryInfo.delivery_time_actual != null ? `${deliveryInfo.delivery_time_actual} min` : 'Pending'}</Typography>
							</Stack>
						)}
					</Stack>
				</CardContent>
			</Card>
		</Box>
	);
};

export default DeliveryInfoPage;
