import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LoadingSpinner } from './components/LoadingSpinner';
import HomePage from './features/home/HomePage';

const CommanderSelectPage = lazy(() => import('./features/commanders/CommanderSelectPage'));
const DeckBuilderPage = lazy(() => import('./features/deck-builder/DeckBuilderPage'));
const CardSearchPage = lazy(() => import('./features/card-search/CardSearchPage'));
const CardDetailPage = lazy(() => import('./features/cards/CardDetailPage'));
const CollectionPage = lazy(() => import('./features/collection/CollectionPage'));

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <Layout>
            <Suspense fallback={<div className="flex justify-center py-20"><LoadingSpinner size="lg" /></div>}>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/commanders" element={<CommanderSelectPage />} />
                <Route path="/deck-builder/:commander" element={<DeckBuilderPage />} />
                <Route path="/cards" element={<CardSearchPage />} />
                <Route path="/cards/:name" element={<CardDetailPage />} />
                <Route path="/collection" element={<CollectionPage />} />
              </Routes>
            </Suspense>
          </Layout>
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
