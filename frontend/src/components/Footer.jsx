import React from 'react';
import { Leaf, Github } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="py-12" style={{ backgroundColor: 'var(--gray-900)' }}>
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--green-mid)' }}>
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-black text-white">CropSense AI</span>
          </div>
          
          <div className="text-center text-gray-400">
            <p className="text-sm">
              Built with 🌱 by the CropSense AI Team · FOAI Group Project
            </p>
            <p className="text-xs mt-2">
              Model: MobileNetV2 · Advisory: Claude AI · Accuracy: 95.41%
            </p>
          </div>
          
          <a 
            href="https://github.com/rwitankar-byte/Harvest_health" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            data-testid="github-link"
          >
            <Github className="w-5 h-5" />
            <span className="text-sm font-bold">View on GitHub</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;