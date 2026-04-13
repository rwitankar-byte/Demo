import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Trash2, ChevronRight, Leaf, AlertTriangle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/history`);
      setHistory(res.data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteRecord = async (id, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/history/${id}`);
      setHistory(prev => prev.filter(r => r.id !== id));
      if (selectedRecord?.id === id) setSelectedRecord(null);
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const clearAll = async () => {
    if (!window.confirm('Clear all diagnosis history?')) return;
    try {
      await axios.delete(`${API}/history`);
      setHistory([]);
      setSelectedRecord(null);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  };

  const getSeverityStyle = (severity) => {
    const styles = {
      'Healthy': { bg: 'var(--green-pale)', text: 'var(--green-dark)', border: 'var(--green-light)' },
      'Mild': { bg: 'var(--teal-light)', text: 'var(--teal)', border: 'rgba(0,105,92,0.2)' },
      'Moderate': { bg: 'rgba(230,81,0,0.1)', text: 'var(--amber)', border: 'rgba(230,81,0,0.2)' },
      'Severe': { bg: 'rgba(198,40,40,0.1)', text: 'var(--red)', border: 'rgba(198,40,40,0.2)' }
    };
    return styles[severity] || styles['Mild'];
  };

  const formatDate = (ts) => {
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const langLabel = { en: 'English', hi: 'Hindi', mr: 'Marathi' };

  return (
    <div className="min-h-screen" data-testid="history-page">
      <Navbar isAppPage={true} />
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-black" style={{ color: 'var(--gray-900)' }} data-testid="history-title">
              Diagnosis History
            </h1>
            <p className="text-gray-600 mt-2">{history.length} past diagnos{history.length === 1 ? 'is' : 'es'} saved</p>
          </div>
          <div className="flex gap-3">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-bold border-2 transition-all duration-300"
              style={{ borderColor: 'var(--green-mid)', color: 'var(--green-mid)' }}
              data-testid="back-to-app-btn"
            >
              <ArrowLeft className="w-4 h-4" /> Back to App
            </Link>
            {history.length > 0 && (
              <button
                onClick={clearAll}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-bold border-2 border-red-300 text-red-600 hover:bg-red-50 transition-all"
                data-testid="clear-all-btn"
              >
                <Trash2 className="w-4 h-4" /> Clear All
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <div className="text-center py-20 text-gray-500">Loading history...</div>
        ) : history.length === 0 ? (
          <div className="text-center py-20" data-testid="history-empty">
            <div className="w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-4" style={{ backgroundColor: 'var(--green-pale)' }}>
              <Clock className="w-12 h-12" style={{ color: 'var(--green-mid)' }} />
            </div>
            <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--gray-900)' }}>No History Yet</h3>
            <p className="text-gray-600 mb-6">Your past diagnoses will appear here after you analyze leaf images</p>
            <Link
              to="/app"
              className="inline-flex items-center gap-2 px-8 py-3 rounded-full font-bold text-white transition-all shadow-lg"
              style={{ backgroundColor: 'var(--green-mid)' }}
            >
              Start Analyzing <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        ) : (
          <div className="grid lg:grid-cols-5 gap-6">
            {/* History list */}
            <div className="lg:col-span-2 space-y-3" data-testid="history-list">
              {history.map((record) => {
                const sev = getSeverityStyle(record.severity);
                const isSelected = selectedRecord?.id === record.id;
                return (
                  <div
                    key={record.id}
                    onClick={() => setSelectedRecord(record)}
                    className={`bg-white rounded-2xl p-5 border cursor-pointer transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md ${
                      isSelected ? 'ring-2 shadow-md' : ''
                    }`}
                    style={{
                      borderColor: isSelected ? 'var(--green-mid)' : 'var(--green-light)',
                      ringColor: 'var(--green-mid)'
                    }}
                    data-testid={`history-item-${record.id}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-base truncate" style={{ color: 'var(--gray-900)' }}>
                          {record.disease_label}
                        </h4>
                        <div className="flex items-center gap-2 mt-2">
                          <span
                            className="text-xs font-bold px-3 py-1 rounded-full border"
                            style={{ backgroundColor: sev.bg, color: sev.text, borderColor: sev.border }}
                          >
                            {record.severity}
                          </span>
                          <span className="text-xs text-gray-500">{(record.confidence * 100).toFixed(0)}%</span>
                          {record.language !== 'en' && (
                            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-200">
                              {langLabel[record.language] || record.language}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
                          <Clock className="w-3 h-3" />
                          {formatDate(record.timestamp)}
                        </div>
                      </div>
                      <button
                        onClick={(e) => deleteRecord(record.id, e)}
                        className="ml-2 p-2 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                        data-testid={`delete-record-${record.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Detail panel */}
            <div className="lg:col-span-3">
              {selectedRecord ? (
                <div className="bg-white rounded-2xl p-8 shadow-lg border sticky top-24" style={{ borderColor: 'var(--green-light)' }} data-testid="history-detail">
                  <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--gray-900)' }}>
                    {selectedRecord.disease_label}
                  </h3>
                  <div className="flex items-center gap-3 mb-4">
                    <span
                      className="text-sm font-bold px-4 py-1.5 rounded-full border"
                      style={(() => { const s = getSeverityStyle(selectedRecord.severity); return { backgroundColor: s.bg, color: s.text, borderColor: s.border }; })()}
                    >
                      {selectedRecord.severity}
                    </span>
                    <span className="text-sm font-bold" style={{ color: 'var(--green-mid)' }}>
                      {(selectedRecord.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
                      <h4 className="font-bold mb-1 flex items-center gap-2" style={{ color: 'var(--gray-900)' }}>
                        <AlertTriangle className="w-4 h-4" style={{ color: 'var(--green-mid)' }} /> Symptoms
                      </h4>
                      <p className="text-sm text-gray-700">{selectedRecord.visible_symptoms}</p>
                    </div>
                    <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
                      <h4 className="font-bold mb-1" style={{ color: 'var(--gray-900)' }}>Cause</h4>
                      <p className="text-sm text-gray-700">{selectedRecord.likely_cause}</p>
                    </div>
                    <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
                      <h4 className="font-bold mb-1" style={{ color: 'var(--gray-900)' }}>Treatment</h4>
                      <p className="text-sm text-gray-700 whitespace-pre-line">{selectedRecord.treatment}</p>
                    </div>
                    <div className="p-4 rounded-xl border" style={{ backgroundColor: 'var(--green-pale)', borderColor: 'var(--green-light)' }}>
                      <h4 className="font-bold mb-1" style={{ color: 'var(--gray-900)' }}>Prevention</h4>
                      <p className="text-sm text-gray-700 whitespace-pre-line">{selectedRecord.preventive_measures}</p>
                    </div>
                  </div>

                  <div className="p-5 rounded-xl" style={{ backgroundColor: 'var(--teal-light)' }}>
                    <h4 className="font-bold mb-2 flex items-center gap-2" style={{ color: 'var(--gray-900)' }}>
                      <Leaf className="w-4 h-4" style={{ color: 'var(--teal)' }} /> Farmer Advisory
                    </h4>
                    <p className="text-sm text-gray-700 leading-relaxed">{selectedRecord.plain_language_advisory}</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full min-h-[400px]">
                  <div className="text-center text-gray-400">
                    <Leaf className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="font-bold text-lg">Select a diagnosis to view details</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
