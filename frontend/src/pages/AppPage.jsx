import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import UploadPanel from '../components/UploadPanel';
import ResultsPanel from '../components/ResultsPanel';
import { API } from '../lib/api';

const LANGUAGES = [
  { code: 'en', label: 'English', flag: 'EN' },
  { code: 'hi', label: 'Hindi', flag: 'HI' },
  { code: 'mr', label: 'Marathi', flag: 'MR' }
];

const AppPage = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [result, setResult] = useState(null);
  const [language, setLanguage] = useState('en');

  const handleAnalyze = async (imageFile, cropName, previewUrl) => {
    try {
      setIsAnalyzing(true);
      setAnalysisStep(1);
      setResult(null);

      // Step 1: Classify disease
      setAnalysisStep(2);
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('crop_name', cropName);

      const classifyResponse = await axios.post(`${API}/classify`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const classification = classifyResponse.data;

      // Step 2: Get advisory (with language)
      setAnalysisStep(3);
      const imageBase64 = previewUrl.split(',')[1];

      const advisoryResponse = await axios.post(`${API}/advisory`, {
        crop_name: cropName,
        disease_label: classification.label,
        confidence: classification.confidence,
        image_base64: imageBase64,
        language: language
      });
      const advisory = advisoryResponse.data;

      const combinedResult = { classification, advisory };
      setResult(combinedResult);

      // Auto-save to history
      try {
        await axios.post(`${API}/history`, {
          crop_name: cropName,
          disease_label: classification.label,
          confidence: classification.confidence,
          severity: advisory.severity,
          visible_symptoms: advisory.visible_symptoms,
          likely_cause: advisory.likely_cause,
          treatment: advisory.treatment,
          preventive_measures: advisory.preventive_measures,
          plain_language_advisory: advisory.plain_language_advisory,
          language: language
        });
      } catch (saveErr) {
        console.warn('Failed to save to history:', saveErr);
      }

      setIsAnalyzing(false);
      setAnalysisStep(0);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze image. Please try again.');
      setIsAnalyzing(false);
      setAnalysisStep(0);
    }
  };

  return (
    <div className="min-h-screen" data-testid="app-page">
      <Navbar isAppPage={true} />
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
        {/* Language selector */}
        <div className="flex items-center justify-end mb-6 gap-2">
          <span className="text-sm font-bold" style={{ color: 'var(--gray-900)' }}>Advisory Language:</span>
          <div className="flex gap-1.5" data-testid="language-selector">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`px-4 py-2 rounded-full text-sm font-bold transition-all duration-300 border ${
                  language === lang.code
                    ? 'text-white shadow-md'
                    : 'text-gray-600 border-gray-300 hover:border-green-400 bg-white'
                }`}
                style={
                  language === lang.code
                    ? { backgroundColor: 'var(--green-mid)', borderColor: 'var(--green-mid)' }
                    : {}
                }
                data-testid={`lang-btn-${lang.code}`}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div>
            <UploadPanel onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
          </div>
          <div>
            <ResultsPanel 
              result={result} 
              isAnalyzing={isAnalyzing} 
              analysisStep={analysisStep}
              language={language}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppPage;
