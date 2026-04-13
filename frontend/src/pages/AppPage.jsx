import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import UploadPanel from '../components/UploadPanel';
import ResultsPanel from '../components/ResultsPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AppPage = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (imageFile, cropName, previewUrl) => {
    try {
      setIsAnalyzing(true);
      setAnalysisStep(1);
      setResult(null);

      // Step 1: Classify disease using HuggingFace
      setAnalysisStep(2);
      const formData = new FormData();
      formData.append('file', imageFile);

      const classifyResponse = await axios.post(`${API}/classify`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const classification = classifyResponse.data;

      // Step 2: Get advisory from Claude AI
      setAnalysisStep(3);
      const imageBase64 = previewUrl.split(',')[1]; // Remove data:image/xxx;base64, prefix

      const advisoryResponse = await axios.post(`${API}/advisory`, {
        crop_name: cropName,
        disease_label: classification.label,
        confidence: classification.confidence,
        image_base64: imageBase64
      });

      const advisory = advisoryResponse.data;

      // Combine results
      setResult({
        classification,
        advisory
      });

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
        <div className="grid lg:grid-cols-2 gap-8">
          <div>
            <UploadPanel onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
          </div>
          
          <div>
            <ResultsPanel 
              result={result} 
              isAnalyzing={isAnalyzing} 
              analysisStep={analysisStep}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppPage;