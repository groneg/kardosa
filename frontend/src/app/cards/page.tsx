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
  is_rookie: boolean;
}

// eslint-disable-next-line @typescript-eslint/no-unused-expressions
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import CardGrid from '../../components/CardGrid';
import { useSwipeable } from 'react-swipeable';

export default function CardsPage() {
  const router = useRouter();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [username, setUsername] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Define the backend API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  // Swipe handlers
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      // Navigate to next page (if available)
      console.log('Swiped left - Next page');
    },
    onSwipedRight: () => {
      // Navigate to previous page
      router.back();
    },
    trackMouse: true,
    preventScrollOnSwipe: true,
    delta: 10, // minimum distance in pixels before a swipe is registered
    swipeDuration: 500, // maximum time in milliseconds for a swipe
    touchEventOptions: { passive: false }, // better touch handling
  });

  // Filter cards based on search query
  const filteredCards = cards.filter(card => {
    const searchLower = searchQuery.toLowerCase();
    return (
      card.player_name.toLowerCase().includes(searchLower) ||
      (card.team && card.team.toLowerCase().includes(searchLower)) ||
      (searchLower === 'rookie' && card.is_rookie)
    );
  });

  const handleLogout = () => {
    fetch(`${API_URL}/logout`, { 
      method: 'POST', 
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(res => {
          if(res.ok) {
              console.log("Logout successful on backend.");
              setCards([]); // Clear cards data
              setError(null);
              router.push('/login');
          } else {
              console.error("Backend logout failed.");
          }
      })
      .catch(err => {
          console.error("Error during logout fetch:", err);
      });
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/upload-binder`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setUploadSuccess(data.message || 'File uploaded successfully');
      
      // Refresh the cards list after successful upload
      window.location.reload();
    } catch (err) {
      console.error('File upload error:', err);
      setUploadError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setUploading(false);
      // Clear the file input
      e.target.value = '';
    }
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch(`${API_URL}/user`, {
          method: 'GET',
          credentials: 'include'
        });

        if (response.status === 401) {
          router.push('/login');
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        setUsername(data.username);
      } catch (err) {
        console.error('Error fetching user data:', err);
      }
    };

    fetchUserData();
  }, [API_URL, router]);

  useEffect(() => {
    const fetchCards = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_URL}/cards`, {
            method: 'GET',
            credentials: 'include' // Send cookies (like the session cookie)
        });

        if (response.status === 401) {
            setError("You must be logged in to view cards. Please log in.");
            router.push('/login');
            return;
        }

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        setCards(data as Card[]);
      } catch (err) {
        console.error("Failed to fetch cards:", err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchCards();
  }, [API_URL, router]);

  return (
    <div className="min-h-screen bg-gray-100" {...swipeHandlers}>
      <main className="flex flex-col items-center justify-start p-4">
        <div className="w-full max-w-7xl flex justify-between items-center mb-6">
          <h1 className="text-[2.6rem] font-extrabold tracking-tight text-gray-800">{username.toUpperCase()}</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
          >
            Logout
          </button>
        </div>

        {/* --- Upload Section --- */}
        <div className="w-full max-w-7xl mb-6">
          <div className="flex items-center">
            <label 
              htmlFor="binder-upload" 
              className="px-4 py-2 bg-white text-red-500 border-2 border-red-500 rounded-full font-bold text-sm hover:bg-red-50 cursor-pointer"
            >
              Choose Binder Image
            </label>
            <input
              id="binder-upload"
              type="file"
              accept="image/png, image/jpeg, image/webp"
              onChange={handleFileChange}
              disabled={uploading}
              className="hidden"
              title="Upload Binder Page"
            />
            {uploading && <span className="ml-4 text-blue-600">Uploading...</span>}
          </div>
          {uploadError && <p className="text-sm text-red-600 mt-2">Upload Error: {uploadError}</p>}
          {uploadSuccess && <p className="text-sm text-green-600 mt-2">{uploadSuccess}</p>}
          
          <input
            type="text"
            placeholder="Search by player name, team, or 'rookie'..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="mt-4 w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-red-500"
          />
        </div>
        {/* --- End Upload Section --- */}

        {loading && <p>Loading cards...</p>}
        {error && <p className="text-red-500">Error loading cards: {error}</p>}

        {!loading && !error && (
          <div className="w-full max-w-7xl">
            <CardGrid cards={filteredCards} />
          </div>
        )}

        {/* Swipe indicators */}
        <div className="fixed bottom-4 left-0 right-0 flex justify-center gap-4 text-sm text-gray-500 bg-white/80 p-2 rounded-lg shadow-sm">
          <span>← Swipe right to go back</span>
          <span>Swipe left for next page →</span>
        </div>
      </main>
    </div>
  );
} 