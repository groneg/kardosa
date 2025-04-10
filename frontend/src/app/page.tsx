'use client'; // Required for useState and useEffect

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Define the Card type based on your data structure
type Card = {
  id: number;
  player_name: string;
  card_year: number;
  manufacturer: string;
  grade?: string; // Optional
  grading_co?: string; // Optional
  img_url?: string; // Optional
};

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Add state for login status
  const [isLoading, setIsLoading] = useState(true);

  // const router = useRouter(); // Uncomment for redirect

  // Define the backend API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  console.log('Current API_URL:', API_URL); // Log the API URL

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const response = await fetch(`${API_URL}/cards`, {
          method: 'GET',
          credentials: 'include'
        });

        if (response.ok) {
          // User is authenticated, redirect to card collection
          router.push('/cards');
        } else {
          // User is not authenticated, redirect to login
          router.push('/login');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
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
