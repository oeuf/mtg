import { useParams } from 'react-router-dom';

export default function DeckBuilderPage() {
  const { commander } = useParams<{ commander: string }>();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-4">Deck Builder</h1>
      <p className="text-gray-400">
        Building deck for <span className="text-white font-semibold">{commander}</span>
      </p>
    </div>
  );
}
