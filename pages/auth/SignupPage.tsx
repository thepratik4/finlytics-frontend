import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '../../components/ui/Primitives';
import { BarChart3 } from 'lucide-react';

export default function SignupPage() {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [error, setError] = React.useState('');

  const signupMutation = useMutation({
    mutationFn: async () => {
      // --- MOCK SIGNUP START ---
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate delay
      
      return {
        message: "Signup successful",
        user: {
          id: Math.floor(Math.random() * 1000),
          email: email,
          created_at: new Date().toISOString()
        },
        status: 201
      };
      // --- MOCK SIGNUP END ---

      /* Real API Call
      const response = await api.post<AuthResponse>('/auth/signup', { email, password });
      return response.data;
      */
    },
    onSuccess: () => {
      navigate('/login');
    },
    onError: (err: any) => {
      setError(err.message || 'Signup failed');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }
    signupMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-4">
            <div className="mx-auto h-12 w-12 bg-primary-600 rounded-xl flex items-center justify-center">
                <BarChart3 className="text-white h-7 w-7" />
            </div>
            <div>
                <CardTitle className="text-2xl">Create an account</CardTitle>
                <p className="text-sm text-gray-500 mt-2">Start analyzing your financial documents today</p>
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
            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            
            {error && <p className="text-sm text-red-500 bg-red-50 p-2 rounded">{error}</p>}

            <Button type="submit" className="w-full" isLoading={signupMutation.isPending}>
              Create Account
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-500">
              Log in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}