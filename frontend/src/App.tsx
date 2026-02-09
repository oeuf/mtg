import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout';
import { ErrorBoundary } from './components/ErrorBoundary';
import HomePage from './features/home/HomePage';
import CommanderSelectPage from './features/commanders/CommanderSelectPage';
import DeckBuilderPage from './features/deck-builder/DeckBuilderPage';
import CardSearchPage from './features/card-search/CardSearchPage';
import CollectionPage from './features/collection/CollectionPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/commanders" element={<CommanderSelectPage />} />
              <Route path="/deck-builder/:commander" element={<DeckBuilderPage />} />
              <Route path="/cards" element={<CardSearchPage />} />
              <Route path="/collection" element={<CollectionPage />} />
            </Routes>
          </Layout>
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
