import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Loader2, Workflow } from 'lucide-react';

export default function AgentPanel({ agents, status, error }) {
  // Pre-defined pipeline sequence
  const pipeline = [
    { key: 'case_intelligence', name: 'Case Intelligence Agent', desc: 'Parses raw text, extracts symptoms, infers product type' },
    { key: 'context_enrichment', name: 'Context Enrichment Agent', desc: 'Searches FAISS vector database for similar historical cases' },
    { key: 'parts_prediction', name: 'Parts Prediction Agent', desc: 'Synthesizes symptoms and history to predict required parts' },
    { key: 'supply_decision', name: 'Supply Decision Agent', desc: 'Checks inventory, location, and determines auto-order vs reserve' },
    { key: 'feedback_learning', name: 'Feedback & Learning Agent', desc: 'Updates knowledge base and confidence metrics' }
  ];

  return (
    <div className="agent-panel">
      <div className="card-header" style={{ marginBottom: '32px' }}>
        <div>
          <h2 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '4px' }}>
            <Workflow size={20} color="var(--color-ge-light-blue)" />
            Agent Orchestration Pipeline
          </h2>
          <p className="text-secondary" style={{ fontSize: '0.85rem' }}>
            LangGraph sequential pipeline — each node checkpoints its state, so requests are resumable & auditable
          </p>
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--color-error)', borderRadius: '8px', color: 'var(--color-error)', marginBottom: '24px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="pipeline-container">
        {pipeline.map((step, index) => {
          const completedAgent = agents.find(a => a.agent_key === step.key);
          const isCompleted = !!completedAgent;
          const isRunning = status === 'running' && !isCompleted && 
            (index === 0 || agents.find(a => a.agent_key === pipeline[index - 1].key));
          
          return (
            <motion.div 
              key={step.key} 
              className={`agent-row ${isCompleted ? 'completed' : ''}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className={`agent-icon-container ${isCompleted ? 'agent-icon-completed' : (isRunning ? 'agent-icon-running' : 'agent-icon-waiting')}`}>
                {isCompleted ? <Check size={16} /> : (isRunning ? <Loader2 size={16} className="text-ge-light-blue" /> : <span style={{ fontSize: '12px' }}>{index + 1}</span>)}
              </div>
              
              <div className="agent-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>{step.name}</h3>
                  <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>AGENT</span>
                </div>
                
                <p className="text-secondary" style={{ fontSize: '0.85rem', marginBottom: isCompleted ? '12px' : '0' }}>
                  {step.desc}
                </p>
                
                <AnimatePresence>
                  {isCompleted && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      style={{ 
                        backgroundColor: 'rgba(255, 255, 255, 0.03)', 
                        padding: '12px', 
                        borderRadius: '6px',
                        borderLeft: '2px solid var(--color-success)',
                        fontSize: '0.85rem'
                      }}
                    >
                      <strong style={{ color: 'var(--color-success)', display: 'block', marginBottom: '4px' }}>Completed</strong>
                      {completedAgent.summary}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
