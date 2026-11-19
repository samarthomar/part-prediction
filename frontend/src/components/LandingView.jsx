import React from 'react';
import { Bot, Network, Database, Layers, ArrowRight } from 'lucide-react';

export default function LandingView() {
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '16px' }}>AI Parts Recommendation Engine</h2>
        <p className="text-secondary" style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
          Welcome. Enter a service complaint or select a sample from the sidebar to trigger the multi-agent diagnostic pipeline.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '40px' }}>
        <h3 className="card-title mb-4" style={{ justifyContent: 'center' }}>Orchestration Flow</h3>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 0' }}>
          <div style={{ textAlign: 'center' }}>
            <div className="flex-center" style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-border)', margin: '0 auto 12px' }}>
              1
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>Parse Complaint</div>
          </div>
          
          <ArrowRight size={20} className="text-muted" />
          
          <div style={{ textAlign: 'center' }}>
            <div className="flex-center" style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-border)', margin: '0 auto 12px' }}>
              2
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>Find Similar</div>
          </div>
          
          <ArrowRight size={20} className="text-muted" />
          
          <div style={{ textAlign: 'center' }}>
            <div className="flex-center" style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'rgba(74, 144, 217, 0.1)', border: '1px solid var(--color-ge-light-blue)', margin: '0 auto 12px' }}>
              3
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-ge-light-blue)' }}>Predict Parts</div>
          </div>
          
          <ArrowRight size={20} className="text-muted" />
          
          <div style={{ textAlign: 'center' }}>
            <div className="flex-center" style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-border)', margin: '0 auto 12px' }}>
              4
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>Check Inventory</div>
          </div>
          
          <ArrowRight size={20} className="text-muted" />
          
          <div style={{ textAlign: 'center' }}>
            <div className="flex-center" style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--color-success)', margin: '0 auto 12px' }}>
              5
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-success)' }}>Learn & Improve</div>
          </div>
        </div>
      </div>

      <div className="stack-cards">
        <div className="stack-card">
          <Bot size={32} className="text-ge-primary-blue" />
          <div>
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Google Gemini</h4>
            <p className="text-secondary" style={{ fontSize: '0.8rem' }}>Advanced LLM reasoning engine for diagnostics</p>
          </div>
        </div>
        
        <div className="stack-card">
          <Network size={32} className="text-ge-orange" />
          <div>
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>LangGraph</h4>
            <p className="text-secondary" style={{ fontSize: '0.8rem' }}>Stateful multi-agent orchestration pipeline</p>
          </div>
        </div>
        
        <div className="stack-card">
          <Database size={32} className="text-ge-light-blue" />
          <div>
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>FAISS VectorStore</h4>
            <p className="text-secondary" style={{ fontSize: '0.8rem' }}>Semantic search over historical case resolutions</p>
          </div>
        </div>
        
        <div className="stack-card">
          <Layers size={32} className="text-success" />
          <div>
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>5 AI Agents</h4>
            <p className="text-secondary" style={{ fontSize: '0.8rem' }}>Specialized roles for intelligence and supply chain</p>
          </div>
        </div>
      </div>
    </div>
  );
}
