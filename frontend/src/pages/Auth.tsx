import React, { useState } from 'react';
import { TextField, Button, Typography, Box, Tabs, Tab, Alert } from '@mui/material';
import api from '../api';

const AuthPage: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [registerData, setRegisterData] = useState({ username: '', email: '', password: '', role: 'customer' });
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTab(newValue);
    setError('');
    setSuccess('');
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      const res = await api.post('/auth/register', registerData);
      setSuccess('Registration successful!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      const res = await api.post('/auth/login', loginData);
      setSuccess('Login successful!');
      // Save token/cookie if needed
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <Box maxWidth={400} mx="auto" mt={4}>
      <Tabs value={tab} onChange={handleTabChange} centered>
        <Tab label="Login" />
        <Tab label="Register" />
      </Tabs>
      {error && <Alert severity="error">{error}</Alert>}
      {success && <Alert severity="success">{success}</Alert>}
      {tab === 0 ? (
        <form onSubmit={handleLogin}>
          <TextField label="Username" fullWidth margin="normal" required value={loginData.username} onChange={e => setLoginData({ ...loginData, username: e.target.value })} />
          <TextField label="Password" type="password" fullWidth margin="normal" required value={loginData.password} onChange={e => setLoginData({ ...loginData, password: e.target.value })} />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Login</Button>
        </form>
      ) : (
        <form onSubmit={handleRegister}>
          <TextField label="Username" fullWidth margin="normal" required value={registerData.username} onChange={e => setRegisterData({ ...registerData, username: e.target.value })} />
          <TextField label="Email" type="email" fullWidth margin="normal" required value={registerData.email} onChange={e => setRegisterData({ ...registerData, email: e.target.value })} />
          <TextField label="Password" type="password" fullWidth margin="normal" required value={registerData.password} onChange={e => setRegisterData({ ...registerData, password: e.target.value })} />
          <TextField label="Role" fullWidth margin="normal" required value={registerData.role} onChange={e => setRegisterData({ ...registerData, role: e.target.value })} helperText="customer or restaurant_manager" />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Register</Button>
        </form>
      )}
    </Box>
  );
};

export default AuthPage;
