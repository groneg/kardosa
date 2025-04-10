'use client'; // Required for useState and useEffect

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import CardGrid from '../components/CardGrid'; // Adjust path if needed
import Link from 'next/link'; // Keep Link if needed elsewhere

// Define the Card type again (or import from a shared types file later)
interface Card {
  id: number;
  player_name: string;
  card_year: string | null;
  manufacturer: string | null;
  card_number: string | null;
  team: string | null;
  grade: string | null;
  image_url: string | null;
  date_added: string;
  notes: string | null;
}

export default function Home() {
  const router = useRouter();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // const router = useRouter(); // Uncomment for redirect

  // Define the backend API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  console.log('Current API_URL:', API_URL); // Log the API URL

  const handleLogout = () => {
    // Remove JWT token removal
    // localStorage.removeItem('jwtToken');
    // Instead, call the backend logout endpoint
    fetch(`${API_URL}/logout`, { 
      method: 'POST', 
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(res => {
          console.log('Logout response status:', res.status); // Log response status
          if(res.ok) {
              console.log("Logout successful on backend.");
              setCards([]); // Clear cards data
              setError(null);
              // Optionally redirect to login or update UI state
          } else {
              console.error("Backend logout failed.");
              // Maybe show an error to the user
          }
      })
      .catch(err => {
          console.error("Error during logout fetch:", err);
      });
  };

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

  useEffect(() => {
    const fetchCards = async () => {
      setLoading(true);
      setError(null);
      try {
        // Remove token handling
        // const token = localStorage.getItem('jwtToken');
        // if (!token) { ... }

        console.log(`Fetching cards from: ${API_URL}/cards`); // Add logging of URL
        const response = await fetch(`${API_URL}/cards`, {
            method: 'GET',
            // Remove Authorization header
            // headers: {
            //     'Authorization': `Bearer ${token}`
            // },
            credentials: 'include' // Send cookies (like the session cookie)
        });

        console.log('Fetch response status:', response.status); // Log response status

        // Handle 401 Unauthorized (user not logged in according to backend session)
        if (response.status === 401) {
            setError("You must be logged in to view cards. Please log in.");
            // localStorage.removeItem('jwtToken'); // No token to remove
            setCards([]);
            return;
        }

        // Remove JWT-specific 401 handling

        if (!response.ok) {
          // Log more details about the error response
          const errorText = await response.text();
          console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        console.log('Fetched cards:', data); // Log fetched data
        setCards(data as Card[]);
      } catch (err) {
        console.error("Failed to fetch cards:", err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchCards();
  }, [API_URL]); // Dependency array includes API_URL in case it changes

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/upload-binder`, {
        method: 'POST',
        body: formData,
        credentials: 'include', // Send session cookie
        // Note: Don't set 'Content-Type' header, browser does it for FormData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Upload failed: ${response.statusText}`);
      }

      setUploadSuccess(`File ${data.original_filename || 'image'} uploaded successfully. Processing initiated.`);
      // TODO: Add logic to poll for processing status or refresh card list

    } catch (err) {
        console.error("Upload failed:", err);
        setUploadError(err instanceof Error ? err.message : 'An unknown error occurred during upload');
    } finally {
      setUploading(false);
      // Clear the file input for next upload (optional)
      event.target.value = '';
    }
  };

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
