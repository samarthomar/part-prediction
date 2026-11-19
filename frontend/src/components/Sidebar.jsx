import React, { useState, useEffect } from 'react';
import { Play, Trash2 } from 'lucide-react';
import { API_BASE } from '../apiConfig';

const GELogo = ({ height = 40 }) => (
  <svg viewBox="0 0 400 100" height={height} xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(50, 50)">
      <circle cx="0" cy="0" r="42" fill="none" stroke="white" strokeWidth="3"/>
      <circle cx="0" cy="0" r="36" fill="none" stroke="white" strokeWidth="1.5"/>
      <text x="0" y="14" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="bold" fontSize="46" fill="white" letterSpacing="-2">GE</text>
    </g>
    <text x="115" y="58" fontFamily="'Inter', sans-serif" fontWeight="700" fontSize="30" fill="white" letterSpacing="3">GE APPLIANCES</text>
  </svg>
);

export default function Sidebar({ 
  complaintText, setComplaintText, 
  productType, setProductType, 
  model, setModel, 
  onRun, isRunning 
}) {
  const [samples, setSamples] = useState([
    { label: "Fridge Not Cooling", text: "Customer says refrigerator is completely warm. Compressor runs but no cold air. Freezer is thawing out." },
    { label: "Washer Leaking", text: "Water pooling under front load washer during spin cycle. Looks like it's coming from the door area." },
    { label: "AC Not Turning On", text: "HVAC system unresponsive. Thermostat is blank and unit outside isn't spinning." }
  ]);

  useEffect(() => {
    fetch(`${API_BASE}/api/samples`)
      .then(res => res.json())
      .then(data => {
        if (data.samples && data.samples.length > 0) {
          setSamples(data.samples);
        }
      })
      .catch(err => console.log('Using default samples'));
  }, []);

  const handleClearDb = async () => {
    if (window.confirm("Are you sure you want to clear all history?")) {
      try {
        await fetch(`${API_BASE}/api/history`, { method: 'DELETE' });
        alert("Database cleared.");
      } catch (e) {
        console.error(e);
      }
    }
  };

  const productTypes = [
    "Auto-Detect", "Refrigerator", "Washing Machine", 
    "HVAC/Air Conditioner", "Wind Turbine", "Industrial Generator"
  ];

  return (
    <div className="sidebar">
      <div style={{ marginBottom: '24px', opacity: 0.8 }}>
        <GELogo height={24} />
      </div>
      
      <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', fontWeight: 600 }}>New Service Request</h2>
      
      <div className="form-group">
        <label className="form-label">Customer Complaint</label>
        <textarea 
          className="form-textarea"
          placeholder="Describe the issue symptoms, noises, error codes..."
          value={complaintText}
          onChange={(e) => setComplaintText(e.target.value)}
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Product Type</label>
        <select 
          className="form-select"
          value={productType}
          onChange={(e) => setProductType(e.target.value)}
        >
          {productTypes.map(pt => <option key={pt} value={pt}>{pt}</option>)}
        </select>
      </div>
      
      <div className="form-group">
        <label className="form-label">Model Number (Optional)</label>
        <input 
          type="text"
          className="form-input"
          placeholder="e.g. GFE28GYNFS"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </div>
      
      <button 
        className="btn btn-primary" 
        onClick={onRun}
        disabled={isRunning || !complaintText.trim()}
      >
        <Play size={18} />
        {isRunning ? 'Processing...' : 'Run AI Recommendation'}
      </button>
      
      <div style={{ marginTop: '32px', marginBottom: 'auto' }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '12px', textTransform: 'uppercase', fontWeight: 600 }}>Sample Complaints</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {samples.map((s, i) => (
            <button 
              key={i} 
              className="btn-outline"
              onClick={() => setComplaintText(s.text)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
      
      <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid var(--color-border)' }}>
        <button className="btn btn-secondary" style={{ width: '100%', fontSize: '0.8rem', padding: '8px' }} onClick={handleClearDb}>
          <Trash2 size={14} /> Clear Database
        </button>
      </div>
    </div>
  );
}
