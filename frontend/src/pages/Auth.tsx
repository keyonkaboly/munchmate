import React, { useState } from 'react';
import { TextField, Button, Box, Tabs, Tab, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, login } = useAuth();
  const [tab, setTab] = useState(0);
  const [registerData, setRegisterData] = useState({ username: '', email: '', password: '', user_type: 'customer' });
  const [loginData, setLoginData] = useState({ email: '', password: '' });
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
      await register({
        username: registerData.username,
        email: registerData.email,
        password: registerData.password,
        role: registerData.user_type as 'customer' | 'restaurant_manager',
      });
      setSuccess('Registration successful! Please log in now.');
      setTab(0);
      setLoginData({ email: registerData.email, password: '' });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      await login(loginData);
      setSuccess('Login successful! Redirecting...');
      navigate('/');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Login failed');
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
          <TextField label="Email" type="email" fullWidth margin="normal" required value={loginData.email} onChange={e => setLoginData({ ...loginData, email: e.target.value })} />
          <TextField label="Password" type="password" fullWidth margin="normal" required value={loginData.password} onChange={e => setLoginData({ ...loginData, password: e.target.value })} />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Login</Button>
        </form>
      ) : (
        <form onSubmit={handleRegister}>
          <TextField label="Username" fullWidth margin="normal" required value={registerData.username} onChange={e => setRegisterData({ ...registerData, username: e.target.value })} />
          <TextField label="Email" type="email" fullWidth margin="normal" required value={registerData.email} onChange={e => setRegisterData({ ...registerData, email: e.target.value })} />
          <TextField label="Password" type="password" fullWidth margin="normal" required value={registerData.password} onChange={e => setRegisterData({ ...registerData, password: e.target.value })} />
          <TextField label="Role" fullWidth margin="normal" required value={registerData.user_type} onChange={e => setRegisterData({ ...registerData, user_type: e.target.value })} helperText="customer or restaurant_manager" />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Register</Button>
        </form>
      )}
    </Box>
  );
};
export default AuthPage;