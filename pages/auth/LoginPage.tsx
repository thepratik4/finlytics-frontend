import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '../../components/ui/Primitives';
import { BarChart3, Info } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  // Clear initial state
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');

  const loginMutation = useMutation({
    mutationFn: async () => {
      const { default: api } = await import('../../services/api');
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    },
    onSuccess: (data) => {
      if (data.access_token) {
        setAuth(data.user, data.access_token);
        navigate('/dashboard/upload');
      }
    },
    onError: (err: any) => {
      setError(err.message || err.response?.data?.message || 'Login failed');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-xl flex items-center justify-center">
            <BarChart3 className="text-white h-7 w-7" />
          </div>
          <div>
            <CardTitle className="text-2xl">Welcome back</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Enter your credentials to access Finlytics</p>
          </div>
        </CardHeader>
        <CardContent>



          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error && <p className="text-sm text-red-500 bg-red-50 p-2 rounded">{error}</p>}

            <Button type="submit" className="w-full" isLoading={loginMutation.isPending}>
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link to="/signup" className="font-semibold text-primary-600 hover:text-primary-500">
              Sign up
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}