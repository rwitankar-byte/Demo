import React from 'react';
import { Upload, Brain, FileText } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    {
      icon: Upload,
      title: 'Upload Photo',
      description: 'Take a clear photo of the affected leaf and upload it to our platform'
    },
    {
      icon: Brain,
      title: 'AI Identifies Disease',
      description: 'Our advanced AI model analyzes the image and identifies the disease with 95.41% accuracy'
    },
    {
      icon: FileText,
      title: 'Get Treatment Advice',
      description: 'Receive detailed treatment steps, prevention measures, and plain-language farmer advisory'
    }
  ];

  return (
    <section id="how-it-works" className="py-20" style={{ backgroundColor: 'var(--green-pale)' }}>
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-4" style={{ backgroundColor: 'white', color: 'var(--green-dark)' }}>
            <span className="text-xs font-bold uppercase tracking-wider">Simple Process</span>
          </div>
          <h2 className="text-4xl lg:text-5xl font-black tracking-tight" style={{ color: 'var(--gray-900)' }} data-testid="how-it-works-title">
            How It Works
          </h2>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">
            Get expert crop disease diagnosis in three simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div 
                key={index} 
                className="bg-white rounded-2xl p-8 shadow-lg border transition-all duration-300 hover:-translate-y-2"
                style={{ borderColor: 'var(--green-light)' }}
                data-testid={`how-it-works-step-${index + 1}`}
              >
                <div className="flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{ backgroundColor: 'var(--green-mid)' }}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <div className="text-6xl font-black mb-4" style={{ color: 'var(--green-pale)' }}>
                  {String(index + 1).padStart(2, '0')}
                </div>
                <h3 className="text-2xl font-bold mb-3" style={{ color: 'var(--gray-900)' }}>
                  {step.title}
                </h3>
                <p className="text-base text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;