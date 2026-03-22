import { useCallback, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { commandersAPI, cardsAPI } from '../../services/api';
import { useDeckBuilder } from './useDeckBuilder';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { DeckList } from '../../components/deck/DeckList';
import { DeckStats } from '../../components/deck/DeckStats';
import { ManaCurve } from '../../components/deck/ManaCurve';
import { RecommendationsPanel } from '../../components/deck/RecommendationsPanel';
import { useToast } from '../../components/ToastContext';

export default function DeckBuilderPage() {
  const { commander: commanderParam } = useParams<{ commander: string }>();
  const { commander, deck, setCommander, addCard, removeCard } = useDeckBuilder();
  const { addToast } = useToast();

  const handleAddCard = useCallback(
    async (cardName: string) => {
      try {
        const { data: card } = await cardsAPI.get(cardName);
        addCard(card);
      } catch (err) {
        console.error('Failed to add card:', err);
        addToast(`Card "${cardName}" not found.`, 'error');
      }
    },
    [addCard, addToast],
  );

  const { data: commanderData, isLoading, isError } = useQuery({
    queryKey: ['commander', commanderParam],
    queryFn: () => commandersAPI.get(commanderParam!).then((r) => r.data),
    enabled: !!commanderParam,
  });

  useEffect(() => {
    if (commanderData) {
      setCommander(commanderData);
    }
  }, [commanderData, setCommander]);

  const deckCardNames = useMemo(() => deck.map((c) => c.name), [deck]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <h1 className="text-3xl font-bold mb-6">Deck Builder</h1>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (isError || !commanderData) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <h1 className="text-3xl font-bold mb-6">Deck Builder</h1>
        <p>Commander not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-2">Deck Builder</h1>
      <p className="text-xl text-gray-300 mb-6">{commanderData.name}</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="mb-6 flex flex-wrap gap-6">
            <DeckStats cards={deck} commander={commander} />
            <ManaCurve cards={deck} />
          </div>
          <DeckList cards={deck} onRemoveCard={removeCard} />
        </div>

        <div>
          <RecommendationsPanel
            commanderName={commanderData.name}
            onAddCard={handleAddCard}
            deckCardNames={deckCardNames}
          />
        </div>
      </div>
    </div>
  );
}
