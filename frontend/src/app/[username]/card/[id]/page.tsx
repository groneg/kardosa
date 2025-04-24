'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';

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

export default function PublicCardDetailPage() {
  const { username, id } = useParams() as { username: string; id: string };
  const [card, setCard] = useState<Card | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCard() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.kardosa.xyz';
        const res = await fetch(`${apiUrl}/public/collection/${username}/${id}`);
        if (!res.ok) throw new Error('Could not load card');
        const data = await res.json();
        setCard(data.card);
      } catch {
        setError('Could not load card');
      } finally {
        setLoading(false);
      }
    }
    if (username && id) fetchCard();
  }, [username, id]);

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (error || !card) return <div className="p-8 text-center text-red-600">{error || 'Card not found'}</div>;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-xl w-full">
        <h1 className="text-2xl font-extrabold mb-4 text-center">{card.player_name}</h1>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          {card.image_url && (
            <div className="relative w-48 h-72">
              <Image src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}${card.image_url}`} alt={card.player_name} fill style={{objectFit:'cover'}} className="rounded" />
            </div>
          )}
          <div className="flex-1">
            <div className="mb-2"><span className="font-semibold">Year:</span> {card.card_year}</div>
            <div className="mb-2"><span className="font-semibold">Manufacturer:</span> {card.manufacturer}</div>
            <div className="mb-2"><span className="font-semibold">Team:</span> {card.team}</div>
            <div className="mb-2"><span className="font-semibold">Grade:</span> {card.grade}</div>
            <div className="mb-2"><span className="font-semibold">Card #:</span> {card.card_number}</div>
            <div className="mb-2"><span className="font-semibold">Notes:</span> {card.notes}</div>
            <div className="mb-2"><span className="font-semibold">Added:</span> {card.date_added ? new Date(card.date_added).toLocaleDateString() : ''}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
