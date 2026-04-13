import React from 'react';
import { Upload, CloudCog, Tag, Brain, CheckCircle } from 'lucide-react';

const Pipeline = () => {
  const steps = [
    { icon: Upload, label: 'Upload' },
    { icon: CloudCog, label: 'HuggingFace API' },
    { icon: Tag, label: 'Disease Label' },
    { icon: Brain, label: 'Claude AI' },
    { icon: CheckCircle, label: 'Result' }
  ];

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-4" style={{ backgroundColor: 'var(--green-pale)', color: 'var(--green-dark)' }}>
            <span className="text-xs font-bold uppercase tracking-wider">Technology Pipeline</span>
          </div>
          <h2 className="text-4xl lg:text-5xl font-black tracking-tight" style={{ color: 'var(--gray-900)' }} data-testid="pipeline-title">
            Powered by Advanced AI
          </h2>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">
            Our intelligent pipeline combines cutting-edge models for accurate diagnosis
          </p>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-center gap-6 md:gap-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <React.Fragment key={index}>
                <div 
                  className="flex flex-col items-center"
                  data-testid={`pipeline-step-${index + 1}`}
                >
                  <div 
                    className="w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110"
                    style={{ backgroundColor: 'var(--green-mid)' }}
                  >
                    <Icon className="w-10 h-10 text-white" />
                  </div>
                  <span className="text-sm font-bold mt-3" style={{ color: 'var(--gray-900)' }}>
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden md:block w-16 h-1 rounded-full" style={{ backgroundColor: 'var(--green-light)' }}></div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        <div className="mt-16 grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl p-8 shadow-lg border" style={{ borderColor: 'var(--green-light)' }}>
            <h3 className="text-2xl font-bold mb-4" style={{ color: 'var(--gray-900)' }}>🤗 HuggingFace Model</h3>
            <p className="text-gray-600 mb-4">
              MobileNetV2 trained on PlantVillage dataset with 38 disease classes and 95.41% accuracy
            </p>
            <div className="text-sm font-bold" style={{ color: 'var(--green-mid)' }}>
              linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification
            </div>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg border" style={{ borderColor: 'var(--green-light)' }}>
            <h3 className="text-2xl font-bold mb-4" style={{ color: 'var(--gray-900)' }}>🧠 Claude AI Advisory</h3>
            <p className="text-gray-600 mb-4">
              Powered by Claude Sonnet 4 to generate expert treatment advice and farmer-friendly recommendations
            </p>
            <div className="text-sm font-bold" style={{ color: 'var(--green-mid)' }}>
              claude-sonnet-4-20250514
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pipeline;