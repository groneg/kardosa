import React, { useState } from "react";

export interface Card {
  id: number;
  player: string;
  team: string | null;
  year: string;
  manufacturer: string;
  image_url?: string;
  date_added?: string;
}

interface CardCollectionViewProps {
  cards: Card[];
  readOnly?: boolean;
}

export function CardCollectionView({ cards, readOnly = false }: CardCollectionViewProps) {
  const [search, setSearch] = useState("");
  const filtered = cards.filter(card => {
    const searchLower = search.toLowerCase();
    return (
      card.player.toLowerCase().includes(searchLower) ||
      (card.team?.toLowerCase().includes(searchLower) ?? false) ||
      card.manufacturer.toLowerCase().includes(searchLower) ||
      card.year.includes(searchLower)
    );
  });

  return (
    <div>
      <div className="mb-4 flex flex-col sm:flex-row items-center gap-2">
        <input
          type="text"
          placeholder="Search cards..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="border rounded px-3 py-2 w-full sm:w-72"
        />
        {/* Hide add/edit controls if readOnly */}
        {!readOnly && (
          <button className="bg-blue-600 text-white px-4 py-2 rounded ml-2">Add Card</button>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {filtered.length === 0 ? (
          <p className="text-center text-gray-600 col-span-full">No cards found.</p>
        ) : (
          filtered.map(card => (
            <div key={card.id} className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
              {card.image_url && (
                <img src={card.image_url} alt={card.player} className="w-32 h-48 object-cover mb-2 rounded" />
              )}
              <div className="font-bold text-lg mb-1">{card.player}</div>
              <div className="text-sm text-gray-700">{card.team || <span className="italic text-gray-400">No team</span>}</div>
              <div className="text-sm text-gray-700">{card.manufacturer}</div>
              <div className="text-xs text-gray-500">{card.year}</div>
              <div className="text-xs text-gray-400">Added: {card.date_added ? new Date(card.date_added).toLocaleDateString() : ''}</div>
              {/* Hide edit/delete if readOnly */}
              {!readOnly && (
                <div className="mt-2 flex gap-2">
                  <button className="text-blue-600 underline">Edit</button>
                  <button className="text-red-600 underline">Delete</button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
