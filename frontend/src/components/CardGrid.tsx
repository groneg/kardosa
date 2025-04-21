import React from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

// Define the structure of a Card object (matching backend)
interface Card {
  id: number;
  player_name: string;
  card_year: string | null;
  manufacturer: string | null;
  card_number: string | null;
  team: string | null;
  grade: string | null;
  image_url: string | null;
  date_added: string; // ISO format string
  notes: string | null;
}

interface CardGridProps {
  cards: Card[];
}

const CardGrid: React.FC<CardGridProps> = ({ cards }) => {
  const router = useRouter();
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  if (!cards || cards.length === 0) {
    return <p className="text-center text-gray-500">No cards found.</p>;
  }

  const handleCardClick = (cardId: number) => {
    router.push(`/card/${cardId}`);
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 p-4 text-red-500">
      {cards.map((card) => (
        <div
          key={card.id}
          className="border rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow cursor-pointer bg-white"
          onClick={() => handleCardClick(card.id)}
        >
          <div className="relative w-full h-48">
            {card.image_url ? (
              <Image
                src={`${API_URL}${card.image_url}`}
                alt={`${card.card_year || ''} ${card.manufacturer || ''} ${card.player_name}`}
                fill
                style={{ objectFit: 'cover' }}
                className=""
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            ) : (
              <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400">
                No Image
              </div>
            )}
          </div>
          <div className="p-2 text-sm">
            <p className="font-semibold truncate" title={card.player_name}>{card.player_name}</p>
            <div className="text-sm text-gray-600">
              <p>{card.card_year}</p>
              <p>{card.manufacturer || 'Unknown'}</p>
            </div>
            {card.grade && <p className="text-xs text-blue-500 truncate" title={`Grade: ${card.grade}`}>Grade: {card.grade}</p>}
          </div>
        </div>
      ))}
    </div>
  );
};

export default CardGrid; 