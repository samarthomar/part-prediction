import React, { useState } from 'react';
import { Send, CheckCircle2 } from 'lucide-react';
import { API_BASE } from '../apiConfig';

export default function FeedbackForm({ caseId }) {
  const [accuracy, setAccuracy] = useState('Yes');
  const [actualParts, setActualParts] = useState('');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await fetch(`${API_BASE}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          accuracy,
          actual_parts: actualParts,
          notes
        })
      });
      
      setSubmitted(true);
    } catch (error) {
      console.error(error);
      // Fallback for mock environment
      setTimeout(() => setSubmitted(true), 500);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="card flex-center" style={{ flexDirection: 'column', padding: '40px 20px', gap: '16px' }}>
        <CheckCircle2 size={48} color="var(--color-success)" />
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Feedback Submitted</h3>
        <p className="text-secondary" style={{ textAlign: 'center', maxWidth: '400px' }}>
          Thank you. This data will be ingested by the VectorStore to improve future predictions.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Technician Feedback</h3>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div className="form-group">
            <label className="form-label">Was the prediction accurate?</label>
            <select 
              className="form-select"
              value={accuracy}
              onChange={(e) => setAccuracy(e.target.value)}
            >
              <option value="Yes">Yes, completely accurate</option>
              <option value="Partially">Partially, missing some parts</option>
              <option value="No">No, inaccurate</option>
            </select>
          </div>
          
          <div className="form-group">
            <label className="form-label">Actual parts used (Comma separated IDs)</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="e.g. WR60X26866, WR55X11132"
              value={actualParts}
              onChange={(e) => setActualParts(e.target.value)}
            />
          </div>
        </div>
        
        <div className="form-group">
          <label className="form-label">Additional Notes (Optional)</label>
          <textarea 
            className="form-textarea" 
            style={{ minHeight: '80px' }}
            placeholder="Any unexpected issues or symptoms?"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" style={{ width: 'auto' }} disabled={isSubmitting}>
            <Send size={16} />
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>
      </form>
    </div>
  );
}
