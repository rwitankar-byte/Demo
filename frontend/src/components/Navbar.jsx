import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, Clock } from 'lucide-react';

const Navbar = ({ isAppPage = false }) => {
  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b" style={{ borderColor: 'var(--green-light)' }}>
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2" data-testid="nav-logo">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--green-mid)' }}>
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-black" style={{ color: 'var(--gray-900)' }}>CropSense AI</span>
          </Link>
          
          <div className="flex items-center gap-3">
            {isAppPage && (
              <Link
                to="/history"
                className="hidden sm:inline-flex items-center gap-2 rounded-full px-5 py-2.5 font-bold transition-all duration-300 border hover:shadow-sm"
                style={{ borderColor: 'var(--green-light)', color: 'var(--gray-900)' }}
                data-testid="history-nav-btn"
              >
                <Clock className="w-4 h-4" />
                History
              </Link>
            )}
            
            {isAppPage ? (
              <Link 
                to="/" 
                className="rounded-full px-6 py-2.5 font-bold transition-all duration-300 border-2"
                style={{ color: 'var(--green-mid)', borderColor: 'var(--green-mid)' }}
                data-testid="back-to-home-btn"
              >
                &larr; Back to Home
              </Link>
            ) : (
              <Link 
                to="/app" 
                className="rounded-full px-8 py-3 font-bold transition-all duration-300 shadow-lg transform hover:-translate-y-0.5"
                style={{ backgroundColor: 'var(--green-mid)', color: 'white' }}
                data-testid="try-it-free-btn"
              >
                Try it Free &rarr;
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
