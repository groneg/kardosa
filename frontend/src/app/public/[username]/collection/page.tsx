'use client';

import React, { useEffect, useState } from 'react';

import { useParams } from 'next/navigation';

interface Card {
  id: number;
  name: string;
  team: string;
  player: string;
  year: string;
  image_url?: string;
  created_at?: string;
}

export default function PublicCollectionPage() {
  const { username } = useParams() as { username: string };
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCollection() {
      try {
        const res = await fetch(`/backend/public/collection/${username}`);
        if (!res.ok) throw new Error('Could not load collection');
        const data = await res.json();
        setCards(data.cards);
      } catch {
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
    <main className="max-w-3xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">{username}&apos;s Public Collection</h1>
      {cards.length === 0 ? (
        <p className="text-center text-gray-600">No cards found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {cards.map(card => (
            <div key={card.id} className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
              {card.image_url && <img src={card.image_url} alt={card.name} className="w-32 h-48 object-cover mb-2 rounded" />}
              <div className="font-bold text-lg mb-1">{card.name}</div>
              <div className="text-sm text-gray-700">{card.player}</div>
              <div className="text-sm text-gray-700">{card.team}</div>
              <div className="text-xs text-gray-500">{card.year}</div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
