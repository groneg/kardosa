'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from "next/image";
import { apiRequest } from '@/utils/api';

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
  sport?: string | null;
}

interface AutocompleteOptions {
  player_names: string[];
  manufacturers: string[];
  teams: string[];
  grades: string[];
  leagues?: string[];
}

// Helper function to generate year options
const generateYearOptions = () => {
  const currentYear = new Date().getFullYear();
  const options = [];
  
  // Generate last 40 years
  for (let i = 0; i < 40; i++) {
    const year = currentYear - i;
    const nextYear = year + 1;
    const formattedYear = `${year}-${nextYear.toString().slice(-2)}`;
    options.push(formattedYear);
  }
  
  return options;
};

export default function EditCardPage() {
  const params = useParams();
  const router = useRouter();
  const [card, setCard] = useState<Card | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [autocompleteOptions, setAutocompleteOptions] = useState<AutocompleteOptions>({
    player_names: [],
    manufacturers: [],
    teams: [],
    grades: []
  });
  
  // Define the backend API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  
  // Add touch event handling for swipe navigation
  const touchStartX = useRef<number | null>(null);
  const touchEndX = useRef<number | null>(null);
  
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };
  
  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
  };
  
  const handleTouchEnd = () => {
    if (touchStartX.current === null || touchEndX.current === null) return;
    
    const swipeDistance = touchEndX.current - touchStartX.current;
    const minSwipeDistance = 100; // Minimum distance for a swipe
    
    // If swiped right (positive distance) and distance is greater than minimum
    if (swipeDistance > minSwipeDistance) {
      router.back(); // Navigate back to previous page
    }
    
    // Reset values
    touchStartX.current = null;
    touchEndX.current = null;
  };

  // Fetch card data
  useEffect(() => {
    const fetchCard = async () => {
      try {
        console.log(`Fetching card with ID: ${params.id}`);
        
        const data = await apiRequest(`/cards/${params.id}`);
        console.log('Card data:', data);
        setCard(data);
      } catch (err) {
        console.error('Error fetching card:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchCard();
  }, [params.id]);

  // Fetch autocomplete options
  useEffect(() => {
    const fetchAutocompleteOptions = async () => {
      try {
        const data = await apiRequest('/autocomplete-options');
        setAutocompleteOptions(data);
      } catch (err) {
        console.error('Error fetching autocomplete options:', err);
      }
    };

    fetchAutocompleteOptions();
  }, []);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!card) return;

    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    try {
      const updatedCard = await apiRequest(`/cards/${card.id}`, {
        method: 'PUT',
        body: JSON.stringify(card),
      });
      
      setCard(updatedCard);
      setSaveSuccess(true);
    } catch (err) {
      console.error('Error updating card:', err);
      setSaveError(err instanceof Error ? err.message : 'An error occurred while saving');
    } finally {
      setSaving(false);
    }
  };

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    if (!card) return;
    
    const { name, value } = e.target;
    setCard({
      ...card,
      [name]: value === '' ? null : value
    });
  };

  // Handle card deletion
  const handleDelete = async () => {
    if (!card) return;

    const confirmed = window.confirm('Are you sure you want to delete this card? This action cannot be undone.');
    
    if (confirmed) {
      setIsDeleting(true);
      setDeleteError(null);
      try {
        await apiRequest(`/cards/${card.id}`, {
          method: 'DELETE'
        });

        // On successful deletion, redirect to the home page
        router.push('/'); 
      } catch (err) {
        console.error('Error deleting card:', err);
        setDeleteError(err instanceof Error ? err.message : 'An error occurred while deleting');
        setIsDeleting(false); // Stop loading state on error
      } 
      // No finally block needed for setIsDeleting(false) because successful deletion navigates away
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
  if (!card) return <div className="p-4">Card not found</div>;

  return (
    <main 
      className="flex min-h-screen flex-col items-center p-4 bg-gray-100"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-lg shadow-md p-4 mb-6 relative aspect-w-3 aspect-h-4">
          {card.image_url ? (
            <Image
              src={`${API_URL}${card.image_url}`}
              alt={`${card.card_year || ''} ${card.manufacturer || ''} ${card.player_name}`}
              fill
              style={{ objectFit: 'contain' }}
              className="rounded-lg"
              priority
            />
          ) : (
            <div className="w-full h-64 bg-gray-200 flex items-center justify-center text-gray-400 rounded-lg">
              No Image Available
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Edit Card Details</h2>
          
          {saveSuccess && (
            <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
              Card updated successfully!
            </div>
          )}
          
          {saveError && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
              Error: {saveError}
            </div>
          )}
          
          {deleteError && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
              Error deleting card: {deleteError}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="player_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Player Name *
                </label>
                <input
                  type="text"
                  id="player_name"
                  name="player_name"
                  value={card.player_name || ''}
                  onChange={handleInputChange}
                  list="player_names_list"
                  className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <datalist id="player_names_list">
                  {autocompleteOptions.player_names.map((name) => (
                    <option key={name} value={name} />
                  ))}
                </datalist>
              </div>
              
              <div>
                <label htmlFor="card_year" className="block text-sm font-medium text-gray-700">
                  Year (YYYY-YY)
                </label>
                <select
                  id="card_year"
                  name="card_year"
                  value={card.card_year || ''}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a year</option>
                  {generateYearOptions().map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="manufacturer" className="block text-sm font-medium text-gray-700 mb-1">
                  Manufacturer
                </label>
                <select
                  id="manufacturer"
                  name="manufacturer"
                  value={card.manufacturer || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a manufacturer</option>
                  <option value="Topps">Topps</option>
                  <option value="Panini">Panini</option>
                  <option value="Upper Deck">Upper Deck</option>
                  <option value="Fleer">Fleer</option>
                  <option value="Donruss">Donruss</option>
                  <option value="Hoops">Hoops</option>
                  <option value="SkyBox">SkyBox</option>
                  <option value="Score">Score</option>
                  <option value="Classic">Classic</option>
                  <option value="Press Pass">Press Pass</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="card_number" className="block text-sm font-medium text-gray-700 mb-1">
                  Card Number
                </label>
                <input
                  type="text"
                  id="card_number"
                  name="card_number"
                  value={card.card_number || ''}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label htmlFor="team" className="block text-sm font-medium text-gray-700">
                  Team
                </label>
                <select
                  id="team"
                  name="team"
                  value={card.team || ''}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a team</option>
                  {autocompleteOptions.teams.map((team) => (
                    <option key={team} value={team}>
                      {team}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="grade" className="block text-sm font-medium text-gray-700 mb-1">
                  Grade
                </label>
                <input
                  type="text"
                  id="grade"
                  name="grade"
                  value={card.grade || ''}
                  onChange={handleInputChange}
                  list="grades_list"
                  className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                />
                <datalist id="grades_list">
                  {autocompleteOptions.grades.map((grade) => (
                    <option key={grade} value={grade} />
                  ))}
                </datalist>
              </div>
              
              <div>
                <label htmlFor="sport" className="block text-sm font-medium text-gray-700">
                  League
                </label>
                <select
                  id="sport"
                  name="sport"
                  value={card.sport || ''}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a League</option>
                  <option value="NBA">NBA</option>
                  <option value="MLB">MLB</option>
                </select>
              </div>
            </div>
            
            <div className="mb-4">
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={card.notes || ''}
                onChange={handleInputChange}
                rows={3}
                className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting || saving}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {isDeleting ? 'Deleting...' : 'Delete Card'}
              </button>
              <button
                type="submit"
                disabled={saving || isDeleting}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>

        {/* Add swipe indicator at the bottom */}
        <div className="fixed bottom-4 left-0 right-0 flex justify-center gap-4 text-sm text-gray-500 bg-white/80 p-2 rounded-lg shadow-sm">
          <span>Swipe right to go back →</span>
        </div>
      </div>
    </main>
  );
} 