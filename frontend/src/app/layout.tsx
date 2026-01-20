import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MTG Commander Deck Builder',
  description: 'Build Commander decks with AI-powered recommendations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <nav className="bg-gray-900 text-white p-4">
            <div className="container mx-auto flex gap-6">
              <a href="/" className="font-bold text-xl">MTG KB</a>
              <a href="/build" className="hover:text-blue-400">Build</a>
              <a href="/analyze" className="hover:text-blue-400">Analyze</a>
              <a href="/explore" className="hover:text-blue-400">Explore</a>
            </div>
          </nav>
          <main className="container mx-auto p-4">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
