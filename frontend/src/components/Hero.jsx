import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, ArrowRight } from 'lucide-react';

const Hero = () => {
  const scrollToHowItWorks = (e) => {
    e.preventDefault();
    document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full" style={{ backgroundColor: 'var(--green-pale)', color: 'var(--green-dark)' }}>
              <Leaf className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">AI-Powered Diagnosis</span>
            </div>
            
            <h1 className="text-5xl lg:text-6xl font-black tracking-tight leading-none" style={{ color: 'var(--gray-900)' }} data-testid="hero-title">
              Detect leaf disease
              <span className="block mt-2" style={{ color: 'var(--green-mid)' }}>instantly</span>
            </h1>
            
            <p className="text-lg leading-relaxed text-gray-600 max-w-xl" data-testid="hero-subtitle">
              Upload a photo of your crop leaf and get expert disease diagnosis in seconds. Powered by advanced AI and trusted by farmers worldwide.
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Link 
                to="/app" 
                className="inline-flex items-center gap-2 rounded-full px-8 py-4 font-bold transition-all duration-300 shadow-lg transform hover:-translate-y-1"
                style={{ 
                  backgroundColor: 'var(--green-mid)',
                  color: 'white'
                }}
                data-testid="hero-try-now-btn"
              >
                Try Now <ArrowRight className="w-5 h-5" />
              </Link>
              
              <a 
                href="#how-it-works" 
                onClick={scrollToHowItWorks}
                className="inline-flex items-center gap-2 rounded-full px-8 py-4 font-bold transition-all duration-300 border-2"
                style={{ 
                  backgroundColor: 'white',
                  borderColor: 'var(--green-mid)',
                  color: 'var(--green-mid)'
                }}
                data-testid="hero-how-it-works-btn"
              >
                See How It Works
              </a>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8 border-t" style={{ borderColor: 'var(--green-light)' }}>
              <div data-testid="stat-accuracy">
                <div className="text-3xl font-black" style={{ color: 'var(--green-mid)' }}>95.41%</div>
                <div className="text-sm text-gray-600 mt-1">Accuracy</div>
              </div>
              <div data-testid="stat-classes">
                <div className="text-3xl font-black" style={{ color: 'var(--green-mid)' }}>38</div>
                <div className="text-sm text-gray-600 mt-1">Disease Classes</div>
              </div>
              <div data-testid="stat-speed">
                <div className="text-3xl font-black" style={{ color: 'var(--green-mid)' }}>~5s</div>
                <div className="text-sm text-gray-600 mt-1">Diagnosis</div>
              </div>
              <div data-testid="stat-cost">
                <div className="text-3xl font-black" style={{ color: 'var(--green-mid)' }}>Free</div>
                <div className="text-sm text-gray-600 mt-1">To Use</div>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="rounded-2xl overflow-hidden shadow-2xl">
              <img 
                src="https://images.unsplash.com/photo-1596415340783-e459d0757527?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxmYXJtZXIlMjBmaWVsZCUyMHN1bnNldHxlbnwwfHx8fDE3NzYwNzI5OTV8MA&ixlib=rb-4.1.0&q=85" 
                alt="Healthy crop field"
                className="w-full h-auto"
                data-testid="hero-image"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 w-32 h-32 rounded-full blur-3xl" style={{ backgroundColor: 'var(--green-mid)', opacity: 0.2 }}></div>
            <div className="absolute -top-6 -right-6 w-40 h-40 rounded-full blur-3xl" style={{ backgroundColor: 'var(--teal)', opacity: 0.2 }}></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;