'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiRequest } from '../../utils/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // API_URL is now handled in the apiRequest utility

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      // The backend /login expects 'username' key
      // In a real app, backend might accept 'email' too, or frontend determines type
      const loginPayload = {
        username: email, // Send email as username for now
        password: password,
      };

      const data = await apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify(loginPayload)
      });

      // Login successful
      setSuccess(`Login successful! Redirecting to your collection...`);
      
      // Store the UUID token in localStorage for header-based auth
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
        console.log("Login successful, UUID token stored in localStorage.");
      } else {
        console.log("Login successful, but no token received. Falling back to cookie auth.");
      }

      // Clear form
      setEmail('');
      setPassword('');

      // Redirect to cards page after a short delay to show success message
      setTimeout(() => {
        router.push('/cards');
      }, 1000);

    } catch (err) {
      console.error("Login failed:", err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-100">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Login</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>

          {error && <p className="text-sm text-red-600 text-center">{error}</p>}
          {success && <p className="text-sm text-green-600 text-center">{success}</p>}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </div>
          <div className="text-sm font-medium text-gray-500 dark:text-gray-300 mt-4">
            Not registered? <a href="/register" className="text-red-600 hover:underline dark:text-red-500">Create account</a>
          </div>
          <div className="text-sm font-medium text-gray-500 dark:text-gray-300 mt-4">
            Return to <Link href="/" className="text-red-600 hover:underline dark:text-red-500">Home Page</Link>
          </div>
        </form>
      </div>
    </main>
  );
} 