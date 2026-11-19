import React from 'react';
import { motion } from 'framer-motion';
import { Search, Brain, Package, History, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ResultCards({ results }) {
  if (!results) return null;

  const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: i => ({
      opacity: 1, y: 0,
      transition: { delay: i * 0.15, duration: 0.5, ease: "easeOut" }
    })
  };

  return (
    <div style={{ paddingBottom: '40px' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '24px', borderBottom: '1px solid var(--color-border)', paddingBottom: '16px' }}>
        Recommendation Results
      </h2>

      {/* Card 1: Intelligence */}
      <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants} className="card card-with-accent">
        <div className="card-header">
          <h3 className="card-title"><Search size={18} className="text-ge-primary-blue" /> Case Intelligence</h3>
          <span className="badge badge-neutral">{results.product_type} - {results.model || 'Unknown Model'}</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div>
            <h4 className="text-secondary" style={{ fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>Extracted Symptoms</h4>
            <div className="pill-list mb-4">
              {Array.isArray(results.symptoms) && results.symptoms.length > 0 ? (
                results.symptoms.map((s, i) => <span key={i} className="pill">{s}</span>)
              ) : (
                <span className="text-muted">None extracted</span>
              )}
            </div>
            
            <h4 className="text-secondary" style={{ fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>Urgency</h4>
            {results.urgency === 'High' ? (
              <span className="badge badge-error"><AlertTriangle size={12} style={{ marginRight: '4px' }} /> High Priority</span>
            ) : (
              <span className="badge badge-info">{results.urgency}</span>
            )}
          </div>
          <div>
            <h4 className="text-secondary" style={{ fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>AI Summary</h4>
            <p style={{ backgroundColor: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '8px', fontSize: '0.9rem' }}>
              {results.issue_summary}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Card 2: Context */}
      <motion.div custom={1} initial="hidden" animate="visible" variants={cardVariants} className="card card-with-accent">
        <div className="card-header">
          <h3 className="card-title"><History size={18} className="text-ge-primary-blue" /> Similar Historical Cases</h3>
          <span className="text-secondary" style={{ fontSize: '0.85rem' }}>{results.similar_cases?.length || 0} matches found</span>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {Array.isArray(results.similar_cases) && results.similar_cases.length > 0 ? (
            results.similar_cases.map((sc, i) => {
              const meta = sc.metadata || {};
              const score = sc.score !== undefined ? sc.score : (sc.match_score || 0);
              const scorePercent = score <= 1 ? (score * 100).toFixed(0) : score; // handle both 0.85 and 85
              const partsUsedStr = meta.parts_used || '';
              return (
              <div key={i} style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                <div className="flex-between mb-2">
                  <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{meta.issue_category || sc.complaint || 'Repair Case'}</span>
                  <span className="badge badge-success">{scorePercent}% Match</span>
                </div>
                <div className="text-secondary" style={{ fontSize: '0.8rem' }}>
                  <strong>Parts used:</strong> {partsUsedStr} | <strong>Resolution:</strong> {meta.resolution_time_hours || 0} hours
                  {meta.fix_successful === 'True' && <span style={{ color: 'var(--color-success)', marginLeft: '8px' }}>✓ Successful Fix</span>}
                </div>
              </div>
            )})
          ) : (
             <p className="text-muted">No highly similar cases found in database.</p>
          )}
        </div>
      </motion.div>

      {/* Card 3: Parts Prediction */}
      <motion.div custom={2} initial="hidden" animate="visible" variants={cardVariants} className="card card-with-accent">
        <div className="card-header">
          <h3 className="card-title"><Brain size={18} className="text-ge-primary-blue" /> Parts Prediction</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {Array.isArray(results.predicted_parts) && results.predicted_parts.map((part, i) => {
            const conf = part.confidence_percent !== undefined ? part.confidence_percent : (part.confidence || 0) * 100;
            return (
            <div key={i} style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
              <div className="flex-between">
                <div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>{part.part_name?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                  <span className="text-secondary" style={{ fontSize: '0.8rem' }}>ID: {part.part_id} | {part.part_description || part.specification || 'N/A'}</span>
                </div>
                <div style={{ textAlign: 'right', width: '120px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-success)' }}>
                    {Number(conf).toFixed(0)}%
                  </div>
                  <div className="progress-bar-container">
                    <motion.div 
                      className="progress-bar-fill" 
                      style={{ backgroundColor: 'var(--color-success)' }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Number(conf)}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                    />
                  </div>
                </div>
              </div>
              <p className="mt-4 text-secondary" style={{ fontSize: '0.85rem' }}>
                <strong>AI Reasoning:</strong> {part.reasoning}
              </p>
            </div>
          )})}
        </div>
      </motion.div>

      {/* Card 4: Supply Decision */}
      <motion.div custom={3} initial="hidden" animate="visible" variants={cardVariants} className="card card-with-accent">
        <div className="card-header">
          <h3 className="card-title"><Package size={18} className="text-ge-primary-blue" /> Supply Chain & Fulfillment</h3>
        </div>
        
        <div>
          {Array.isArray(results.supply_decisions) && results.supply_decisions.map((decision, i) => {
            const qty = decision.stock_quantity ?? decision.stock ?? decision.quantity ?? 0;
            const loc = decision.warehouse_location || decision.warehouse || decision.location || 'N/A';
            const cost = decision.unit_cost_inr ?? decision.unit_cost ?? 0;
            const dec = (decision.decision || '').toUpperCase();
            const partNameRaw = decision.part_name || decision.part_id || 'N/A';
            
            return (
            <div key={i} className="part-detail">
              <div className="part-image flex-center" style={{ overflow: 'hidden' }}>
                {decision.image_url ? (
                  <img src={decision.image_url} alt="part" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                ) : (
                  <Package size={40} color="#ccc" />
                )}
              </div>
              <div className="part-info">
                <div className="flex-between">
                  <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>{partNameRaw.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} <span style={{fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginLeft:'8px'}}>({decision.part_id})</span></h4>
                  {dec.includes('AUTO') ? (
                     <span className="badge badge-success">AUTO ORDER</span>
                  ) : dec.includes('RESERVE') ? (
                     <span className="badge badge-warning">RESERVE</span>
                  ) : (
                     <span className="badge badge-error">ESCALATE</span>
                  )}
                </div>
                
                <div className="part-metrics">
                  <div className="part-metric">
                    <span className="part-metric-label">Stock</span>
                    <span className="part-metric-value">{qty} units</span>
                  </div>
                  <div className="part-metric">
                    <span className="part-metric-label">Location</span>
                    <span className="part-metric-value">{loc}</span>
                  </div>
                  <div className="part-metric">
                    <span className="part-metric-label">Unit Cost</span>
                    <span className="part-metric-value">INR {Number(cost).toLocaleString()}</span>
                  </div>
                  <div className="part-metric">
                    <span className="part-metric-label">Lead Time</span>
                    <span className="part-metric-value">{decision.lead_time_days || 0} days</span>
                  </div>
                </div>
              </div>
            </div>
          )})}
        </div>
      </motion.div>

      {/* Card 5: Feedback Learning */}
      <motion.div custom={4} initial="hidden" animate="visible" variants={cardVariants} className="card card-with-accent">
        <div className="card-header">
          <h3 className="card-title"><ShieldCheck size={18} className="text-ge-primary-blue" /> Continuous Learning</h3>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div className="text-secondary" style={{ fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Accuracy Target</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-success)' }}>92%</div>
          </div>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div className="text-secondary" style={{ fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Parts Predicted</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{Array.isArray(results.predicted_parts) ? results.predicted_parts.length : 0}</div>
          </div>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div className="text-secondary" style={{ fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Avg Confidence</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              {Array.isArray(results.predicted_parts) && results.predicted_parts.length > 0 
                ? (results.predicted_parts.reduce((a,b)=>{
                    const c = b.confidence_percent !== undefined ? b.confidence_percent : (b.confidence || 0) * 100;
                    return a + Number(c);
                  }, 0) / results.predicted_parts.length).toFixed(0) + '%'
                : 'N/A'
              }
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
            <div className="text-secondary" style={{ fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>VectorStore</div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-ge-light-blue)', marginTop: '8px' }}>Indexed</div>
          </div>
        </div>
      </motion.div>

    </div>
  );
}
