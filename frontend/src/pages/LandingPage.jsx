import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import HowItWorks from '../components/HowItWorks';
import Pipeline from '../components/Pipeline';
import Footer from '../components/Footer';

const LandingPage = () => {
  return (
    <div className="min-h-screen" data-testid="landing-page">
      <Navbar />
      <Hero />
      <HowItWorks />
      <Pipeline />
      <Footer />
    </div>
  );
};

export default LandingPage;