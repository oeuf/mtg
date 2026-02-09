import { NavLink } from 'react-router-dom';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/commanders', label: 'Commanders' },
  { to: '/cards', label: 'Cards' },
  { to: '/deck-builder/select', label: 'Deck Builder' },
  { to: '/collection', label: 'Collection' },
];

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-gray-800 border-b border-gray-700">
      <nav className="max-w-7xl mx-auto px-4 flex items-center h-14 gap-8">
        <NavLink to="/" className="text-lg font-bold text-white shrink-0">
          MTG Commander
        </NavLink>
        <ul className="flex items-center gap-1">
          {navLinks.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `px-3 py-2 rounded text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-brand-500 bg-gray-700/50'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700/30'
                  }`
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
