import React, { useState, useRef } from 'react';
import { Upload, X, Loader2 } from 'lucide-react';

const UploadPanel = ({ onAnalyze, isAnalyzing }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const crops = ['Tomato', 'Potato', 'Wheat', 'Corn', 'Apple', 'Pepper', 'Other'];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = () => {
    if (selectedImage) {
      onAnalyze(selectedImage, selectedCrop, previewUrl);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2" style={{ color: 'var(--gray-900)' }} data-testid="upload-panel-title">
          Upload Leaf Image
        </h2>
        <p className="text-gray-600">Upload a clear photo of the affected crop leaf for analysis</p>
      </div>

      <div
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
          dragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-green-400'
        }`}
        style={!dragActive ? { borderColor: 'rgba(56, 142, 60, 0.3)', backgroundColor: 'var(--green-pale)' } : {}}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !previewUrl && fileInputRef.current?.click()}
        data-testid="upload-zone"
      >
        {previewUrl ? (
          <div className="relative">
            <img src={previewUrl} alt="Preview" className="max-h-96 mx-auto rounded-lg" data-testid="image-preview" />
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleRemoveImage();
              }}
              className="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors"
              data-testid="remove-image-btn"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--green-mid)' }}>
              <Upload className="w-10 h-10 text-white" />
            </div>
            <div>
              <p className="text-lg font-bold" style={{ color: 'var(--gray-900)' }}>
                Drag and drop your image here
              </p>
              <p className="text-sm text-gray-600 mt-2">or click to browse</p>
            </div>
            <p className="text-xs text-gray-500">Supports: JPG, PNG, WEBP</p>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileInput}
          data-testid="file-input"
        />
      </div>

      <div>
        <label className="block text-sm font-bold mb-3" style={{ color: 'var(--gray-900)' }}>
          Select Crop Type
        </label>
        <div className="flex flex-wrap gap-2">
          {crops.map((crop) => (
            <button
              key={crop}
              onClick={() => setSelectedCrop(crop)}
              className={`px-4 py-2 rounded-full text-sm font-bold transition-all duration-300 border ${
                selectedCrop === crop
                  ? 'border-green-500 text-white'
                  : 'border-gray-300 text-gray-600 hover:border-green-400'
              }`}
              style={
                selectedCrop === crop
                  ? { backgroundColor: 'var(--green-mid)', borderColor: 'var(--green-mid)' }
                  : {}
              }
              data-testid={`crop-chip-${crop.toLowerCase()}`}
            >
              {crop}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!selectedImage || isAnalyzing}
        className="w-full rounded-full px-8 py-4 font-bold transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        style={{
          backgroundColor: 'var(--green-mid)',
          color: 'white'
        }}
        data-testid="analyze-btn"
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing...
          </>
        ) : (
          'Analyze Disease'
        )}
      </button>
    </div>
  );
};

export default UploadPanel;