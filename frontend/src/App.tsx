import React from 'react';
import { ErrorBoundary } from './components';
import { HomePage } from './pages';

function App() {
  return (
    <ErrorBoundary>
      <HomePage />
    </ErrorBoundary>
  );
}

export default App;
