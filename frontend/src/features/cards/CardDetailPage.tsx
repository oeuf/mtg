import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { cardsAPI } from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Badge } from '../../components/ui/Badge';
import { SimilarCards } from './SimilarCards';
import { SynergyCards } from './SynergyCards';
import { CombosList } from './CombosList';

export default function CardDetailPage() {
  const { name } = useParams<{ name: string }>();

  const { data: card, isLoading, isError } = useQuery({
    queryKey: ['card', name],
    queryFn: () => cardsAPI.get(name!).then((r) => r.data),
    enabled: !!name,
  });

  const { data: similarData } = useQuery({
    queryKey: ['card-similar', name],
    queryFn: () => cardsAPI.getSimilar(name!).then((r) => r.data),
    enabled: !!name,
  });

  const { data: synergiesData } = useQuery({
    queryKey: ['card-synergies', name],
    queryFn: () => cardsAPI.getSynergies(name!).then((r) => r.data),
    enabled: !!name,
  });

  const { data: combosData } = useQuery({
    queryKey: ['card-combos', name],
    queryFn: () => cardsAPI.getCombos(name!).then((r) => r.data),
    enabled: !!name,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (isError || !card) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <Link to="/cards" className="text-brand-400 hover:underline mb-4 inline-block">
          &larr; Back to Search
        </Link>
        <p className="text-gray-400">Card not found.</p>
      </div>
    );
  }

  const similarCards = similarData?.similar_cards ?? [];
  const synergies = synergiesData?.synergies ?? [];
  const combos = combosData?.combos ?? [];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <Link to="/cards" className="text-brand-400 hover:underline mb-4 inline-block">
        &larr; Back to Search
      </Link>

      <div className="mb-8">
        <div className="flex items-start gap-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold">{card.name}</h1>
            <p className="text-gray-400 text-lg">{card.mana_cost}</p>
          </div>
        </div>
        <p className="text-gray-300 mb-2">{card.type_line}</p>
        {card.oracle_text && (
          <p className="text-gray-200 whitespace-pre-line mb-4">{card.oracle_text}</p>
        )}
        {(card.color_identity ?? []).length > 0 && (
          <div className="flex gap-1 mb-4">
            {(card.color_identity ?? []).map((color) => (
              <Badge key={color} variant={`mana-${color}` as 'default'}>
                {color}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-8">
        <section>
          <h2 className="text-xl font-bold mb-4">Similar Cards</h2>
          <SimilarCards cards={similarCards} />
        </section>

        <section>
          <h2 className="text-xl font-bold mb-4">Synergies</h2>
          <SynergyCards cards={synergies} />
        </section>

        <section>
          <h2 className="text-xl font-bold mb-4">Combos</h2>
          <CombosList combos={combos} />
        </section>
      </div>
    </div>
  );
}
