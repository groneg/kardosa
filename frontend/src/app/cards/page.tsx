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
import { apiRequest } from '../../utils/api';

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
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [estimatedTotalTime, setEstimatedTotalTime] = useState<number>(0);
  const [progressIntervalId, setProgressIntervalId] = useState<NodeJS.Timeout | null>(null);
  const [numUploadingFiles, setNumUploadingFiles] = useState<number>(0);

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

  const handleLogout = async () => {
    try {
      await apiRequest('/logout', { method: 'POST' });
      console.log("Logout successful on backend.");
      
      // Clear UUID token from localStorage
      localStorage.removeItem('auth_token');
      
      // Clear app state
      setCards([]); 
      setError(null);
      
      // Redirect to login page
      router.push('/login');
    } catch (err) {
      console.error("Error during logout:", err);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    if (files.length > 5) {
      setUploadError('You can only upload up to 5 binder images at a time.');
      // Clear the file input
      e.target.value = '';
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    setNumUploadingFiles(files.length);
    const totalSeconds = files.length * 20;
    setEstimatedTotalTime(totalSeconds);
    setUploadProgress(0);
    // Simulate progress bar
    let elapsed = 0;
    const interval = setInterval(() => {
      elapsed += 0.5;
      setUploadProgress(Math.min(100, Math.round((elapsed / totalSeconds) * 100)));
      if (elapsed >= totalSeconds) {
        clearInterval(interval);
      }
    }, 500);
    setProgressIntervalId(interval);

    try {
      // Sequentially upload each file
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i]);

        const token = localStorage.getItem('auth_token');
        const headers: HeadersInit = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_URL}/upload-binder`, {
          method: 'POST',
          body: formData,
          headers
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Upload failed: ${response.statusText}`);
        }
      }

      setUploadSuccess('All binder images uploaded successfully');
      window.location.reload();
    } catch (err) {
      console.error('File upload error:', err);
      setUploadError(err instanceof Error ? err.message : 'Failed to upload file(s)');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      setEstimatedTotalTime(0);
      setNumUploadingFiles(0);
      if (progressIntervalId) clearInterval(progressIntervalId);
      // Clear the file input
      e.target.value = '';
    }
  };

  // Clean up interval if component unmounts or uploading changes
  useEffect(() => {
    return () => {
      if (progressIntervalId) clearInterval(progressIntervalId);
    };
  }, [progressIntervalId]);


  // --- Loosie (Single Card) Upload Handler ---
  const handleLoosieFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('auth_token');
      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(`${API_URL}/upload-single-card`, {
        method: 'POST',
        body: formData,
  
        headers
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Upload failed: ${response.statusText}`);
      }
      const data = await response.json();
      setUploadSuccess(data.message || 'Single card uploaded successfully');
      window.location.reload();
    } catch (err) {
      console.error('Single card upload error:', err);
      setUploadError(err instanceof Error ? err.message : 'Failed to upload single card');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };


  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const data = await apiRequest('/user');
        setUsername(data.username);
      } catch (err) {
        console.error('Error fetching user data:', err);
        
        // If authentication fails, redirect to login
        if (err instanceof Error && err.message.includes('401')) {
          router.push('/login');
        }
      }
    };

    fetchUserData();
  }, [API_URL, router]);

  useEffect(() => {
    const fetchCards = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiRequest('/cards');
        setCards(data as Card[]);
      } catch (err) {
        console.error("Failed to fetch cards:", err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        
        // If authentication fails, redirect to login
        if (err instanceof Error && err.message.includes('401')) {
          setError("You must be logged in to view cards. Please log in.");
          router.push('/login');
        }
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
              Choose Binder Images (up to 5)
            </label>
            <input
              id="binder-upload"
              type="file"
              accept="image/png, image/jpeg, image/webp"
              multiple
              onChange={handleFileChange}
              disabled={uploading}
              className="hidden"
              title="Upload up to 5 Binder Images"
            />

            {/* Add Loosies Button */}
            <label
              htmlFor="loosie-upload"
              className="ml-4 px-4 py-2 bg-white text-blue-600 border-2 border-blue-600 rounded-full font-bold text-sm hover:bg-blue-50 cursor-pointer"
            >
              Add Loosies
            </label>
            <input
              id="loosie-upload"
              type="file"
              accept="image/png, image/jpeg, image/webp"
              onChange={handleLoosieFileChange}
              disabled={uploading}
              className="hidden"
              title="Upload Single Card (Loosie)"
            />
          </div>
          {uploading && (
            <div className="mt-2 flex items-center gap-4">
              <div className="w-64 bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-200"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <span className="text-blue-600 text-sm font-semibold">
                Processing ({numUploadingFiles} image{numUploadingFiles !== 1 ? 's' : ''}, ~{estimatedTotalTime}s)
              </span>
            </div>
          )}
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