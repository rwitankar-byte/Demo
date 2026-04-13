import React from 'react';
import { Loader2, CheckCircle, AlertCircle, Info, Leaf } from 'lucide-react';

const ResultsPanel = ({ result, isAnalyzing, analysisStep }) => {
  if (!isAnalyzing && !result) {
    return (
      <div className="flex items-center justify-center h-full min-h-[500px]">
        <div className="text-center space-y-4" data-testid="empty-state">
          <div className="w-24 h-24 mx-auto rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--green-pale)' }}>
            <Leaf className="w-12 h-12" style={{ color: 'var(--green-mid)' }} />
          </div>
          <div>
            <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--gray-900)' }}>
              Ready to Analyze
            </h3>
            <p className="text-gray-600">
              Upload a leaf image to get started with disease detection
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (isAnalyzing) {
    const steps = [
      { id: 1, label: 'Uploading Image', icon: Loader2 },
      { id: 2, label: 'Detecting Disease', icon: Loader2 },
      { id: 3, label: 'Generating Advisory', icon: Loader2 }
    ];

    return (
      <div className="flex items-center justify-center h-full min-h-[500px]">
        <div className="w-full max-w-md space-y-6" data-testid="progress-indicator">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold" style={{ color: 'var(--gray-900)' }}>
              Analyzing Your Crop
            </h3>
            <p className="text-gray-600 mt-2">Please wait while we process your image</p>
          </div>
          
          {steps.map((step) => {
            const Icon = step.icon;
            const isActive = analysisStep >= step.id;
            const isComplete = analysisStep > step.id;
            
            return (
              <div key={step.id} className="flex items-center gap-4" data-testid={`progress-step-${step.id}`}>
                <div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isComplete ? 'bg-green-500' : isActive ? 'bg-green-400' : 'bg-gray-200'
                  }`}
                >
                  {isComplete ? (
                    <CheckCircle className="w-6 h-6 text-white" />
                  ) : isActive ? (
                    <Icon className="w-6 h-6 text-white animate-spin" />
                  ) : (
                    <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                  )}
                </div>
                <div className="flex-1">
                  <div className={`font-bold ${
                    isActive ? 'text-gray-900' : 'text-gray-400'
                  }`}>
                    {step.label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (result) {
    const getSeverityColor = (severity) => {
      const colors = {
        'Healthy': { bg: 'var(--green-pale)', text: 'var(--green-dark)', border: 'var(--green-light)' },
        'Mild': { bg: 'var(--teal-light)', text: 'var(--teal)', border: 'rgba(0, 105, 92, 0.2)' },
        'Moderate': { bg: 'rgba(230, 81, 0, 0.1)', text: 'var(--amber)', border: 'rgba(230, 81, 0, 0.2)' },
        'Severe': { bg: 'rgba(198, 40, 40, 0.1)', text: 'var(--red)', border: 'rgba(198, 40, 40, 0.2)' }
      };
      return colors[severity] || colors['Mild'];
    };

    const severityColors = getSeverityColor(result.advisory?.severity || 'Mild');

    return (
      <div className="space-y-6" data-testid="results-panel">
        <div className="bg-white rounded-2xl p-8 shadow-lg border" style={{ borderColor: 'var(--green-light)' }}>
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h3 className="text-3xl font-bold mb-2" style={{ color: 'var(--gray-900)' }} data-testid="disease-name">
                {result.classification.label}
              </h3>
              <div className="flex items-center gap-3">
                <span 
                  className="inline-block px-4 py-1.5 rounded-full text-sm font-bold border"
                  style={{
                    backgroundColor: severityColors.bg,
                    color: severityColors.text,
                    borderColor: severityColors.border
                  }}
                  data-testid="severity-badge"
                >
                  {result.advisory?.severity || 'Unknown'}
                </span>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold" style={{ color: 'var(--gray-900)' }}>Confidence</span>
              <span className="text-sm font-bold" style={{ color: 'var(--green-mid)' }} data-testid="confidence-score">
                {(result.classification.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-3 rounded-full" style={{ backgroundColor: 'var(--green-pale)' }}>
              <div 
                className="h-full rounded-full transition-all duration-500"
                style={{ 
                  width: `${result.classification.confidence * 100}%`,
                  backgroundColor: 'var(--green-mid)'
                }}
                data-testid="confidence-bar"
              ></div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5" style={{ color: 'var(--green-mid)' }} />
                <h4 className="font-bold" style={{ color: 'var(--gray-900)' }}>Symptoms</h4>
              </div>
              <p className="text-sm text-gray-700" data-testid="symptoms">
                {result.advisory?.visible_symptoms || 'N/A'}
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-5 h-5" style={{ color: 'var(--green-mid)' }} />
                <h4 className="font-bold" style={{ color: 'var(--gray-900)' }}>Cause</h4>
              </div>
              <p className="text-sm text-gray-700" data-testid="cause">
                {result.advisory?.likely_cause || 'N/A'}
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5" style={{ color: 'var(--green-mid)' }} />
                <h4 className="font-bold" style={{ color: 'var(--gray-900)' }}>Treatment</h4>
              </div>
              <p className="text-sm text-gray-700" data-testid="treatment">
                {result.advisory?.treatment || 'N/A'}
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
              <div className="flex items-center gap-2 mb-2">
                <Leaf className="w-5 h-5" style={{ color: 'var(--green-mid)' }} />
                <h4 className="font-bold" style={{ color: 'var(--gray-900)' }}>Prevention</h4>
              </div>
              <p className="text-sm text-gray-700" data-testid="prevention">
                {result.advisory?.preventive_measures || 'N/A'}
              </p>
            </div>
          </div>

          <div className="p-6 rounded-xl" style={{ backgroundColor: 'var(--teal-light)' }}>
            <h4 className="font-bold mb-3 flex items-center gap-2" style={{ color: 'var(--gray-900)' }}>
              <Leaf className="w-5 h-5" style={{ color: 'var(--teal)' }} />
              Farmer Advisory
            </h4>
            <p className="text-gray-700 leading-relaxed" data-testid="advisory">
              {result.advisory?.plain_language_advisory || 'No advisory available'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ResultsPanel;