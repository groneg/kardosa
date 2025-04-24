'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import CardGrid from '@/components/CardGrid';

// Card type matching CardGrid
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

export default function PublicCollectionPage() {
  const { username } = useParams() as { username: string };
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchCollection() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://api.kardosa.xyz";
        const res = await fetch(`${apiUrl}/public/collection/${username}`);
        if (!res.ok) throw new Error('Could not load collection');
        const data = await res.json();
        // Map backend fields to CardGrid Card interface if needed
        setCards(data.cards.map((c: any) => ({
          id: c.id,
          player_name: c.player || c.player_name || '',
          card_year: c.year || c.card_year || null,
          manufacturer: c.manufacturer || null,
          card_number: c.card_number || null,
          team: c.team || null,
          grade: c.grade || null,
          image_url: c.image_url || null,
          date_added: c.date_added || '',
          notes: c.notes || null,
          is_rookie: c.is_rookie || false
        })));
      } catch (err) {
        setError('Could not load collection');
      } finally {
        setLoading(false);
      }
    }
    if (username) fetchCollection();
  }, [username]);

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (error) return <div className="p-8 text-center text-red-600">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="flex flex-col items-center justify-start p-4">
        <div className="w-full max-w-7xl flex flex-col items-center mb-6">
          <h1 className="text-3xl font-bold mb-4 text-center">{username.toUpperCase()}&apos;S CARDS</h1>
          <input
            type="text"
            placeholder="Search cards..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="mb-6 border rounded px-3 py-2 w-full sm:w-72"
          />
        </div>
        <div className="w-full max-w-7xl">
          <CardGrid
            cards={cards.filter(card => {
              const searchLower = searchQuery.toLowerCase();
              return (
                card.player_name.toLowerCase().includes(searchLower) ||
                (card.team && card.team.toLowerCase().includes(searchLower)) ||
                (card.manufacturer && card.manufacturer.toLowerCase().includes(searchLower)) ||
                (card.card_year && card.card_year.includes(searchLower))
              );
            })}
            readOnly={true}
            onCardClick={(cardId: number) => {
              window.location.href = `/${username}/card/${cardId}`;
            }}
          />
        </div>
      </main>
    </div>
  );
}
