import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-8">
      <h1 className="text-5xl font-bold mb-4">MTG Commander</h1>
      <p className="text-gray-400 text-lg mb-8 max-w-xl text-center">
        Build optimized Commander decks with ML-powered synergy analysis and intelligent card recommendations.
      </p>
      <nav className="flex gap-4">
        <Link to="/commanders" className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition">
          Select Commander
        </Link>
        <Link to="/cards" className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 transition">
          Card Search
        </Link>
        <Link to="/collection" className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 transition">
          My Collection
        </Link>
      </nav>
    </div>
  );
}
