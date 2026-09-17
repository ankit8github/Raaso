import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { OnboardingPage } from './pages/OnboardingPage';
import { MatchesPage } from './pages/MatchesPage';
import { SquadPage } from './pages/SquadPage';
import type { Event } from './lib/types';

export const App: React.FC = () => {
  const [activeEvent, setActiveEvent] = useState<Event | null>(null);
  const location = useLocation();

  useEffect(() => {
    const saved = localStorage.getItem('raaso_active_event');
    if (saved) {
      try {
        setActiveEvent(JSON.parse(saved));
      } catch {
        // ignore
      }
    }
  }, [location]);

  return (
    <div className="app-container">
      <Navbar currentEventName={activeEvent ? activeEvent.name : undefined} />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/events/:eventId/onboard" element={<OnboardingPage />} />
          <Route path="/matches" element={<MatchesPage />} />
          <Route path="/squads" element={<SquadPage />} />
          <Route path="*" element={<HomePage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

export default App;

