'use client'; // Required for useState and useEffect

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiRequest } from '@/utils/api';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  // const router = useRouter(); // Uncomment for redirect

  // Define the backend API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  console.log('Current API_URL:', API_URL); // Log the API URL

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        await apiRequest('/cards');
        // If we get here without an error, user is authenticated
        router.push('/cards');
      } catch (error) {
        console.error('Authentication check failed:', error);
        // User is not authenticated, redirect to login
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthentication();
  }, [API_URL, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Checking authentication...</p>
      </div>
    );
  }

  // This will not typically render due to immediate redirect
  return (
    <div className="flex min-h-screen items-center justify-center">
      <p>Redirecting...</p>
    </div>
  );
}
