import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import AgentPanel from './components/AgentPanel'
import ResultCards from './components/ResultCards'
import FeedbackForm from './components/FeedbackForm'
import Dashboard from './components/Dashboard'
import LandingView from './components/LandingView'
import { getWsUrl } from './apiConfig'
import { runClientSimulation } from './simulation'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('recommendation')
  const [complaintText, setComplaintText] = useState('')
  const [productType, setProductType] = useState('Auto-Detect')
  const [model, setModel] = useState('')
  
  const [agentState, setAgentState] = useState({
    status: 'idle', // idle, running, completed, error
    agents: [],
    finalResults: null,
    caseId: null,
    error: null
  })

  const handleRunAI = () => {
    if (!complaintText.trim()) return;
    
    // Reset state
    setAgentState({
      status: 'running',
      agents: [],
      finalResults: null,
      caseId: null,
      error: null
    });
    
    let simulationStarted = false;
    const startFallbackSimulation = () => {
      if (simulationStarted) return;
      simulationStarted = true;
      runClientSimulation({
        complaintText,
        productType,
        model,
        onAgentComplete: (agentData) => {
          setAgentState(prev => ({
            ...prev,
            agents: [...prev.agents, agentData]
          }));
        },
        onComplete: (completeData) => {
          setAgentState(prev => ({
            ...prev,
            status: 'completed',
            caseId: completeData.case_id,
            finalResults: completeData.results
          }));
        }
      });
    };

    try {
      const ws = new WebSocket(getWsUrl());
      const timeoutId = setTimeout(() => {
        if (!simulationStarted && ws.readyState !== WebSocket.OPEN) {
          try { ws.close(); } catch (err) {}
          startFallbackSimulation();
        }
      }, 1500);
      
      ws.onopen = () => {
        clearTimeout(timeoutId);
        ws.send(JSON.stringify({
          complaint_text: complaintText,
          product_type: productType,
          model: model
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'agent_complete') {
          setAgentState(prev => ({
            ...prev,
            agents: [...prev.agents, data]
          }));
        } else if (data.type === 'complete') {
          setAgentState(prev => ({
            ...prev,
            status: 'completed',
            caseId: data.case_id,
            finalResults: data.results
          }));
          ws.close();
        } else if (data.type === 'error') {
          startFallbackSimulation();
        }
      };
      
      ws.onerror = () => {
        clearTimeout(timeoutId);
        startFallbackSimulation();
      };
    } catch (e) {
      console.warn("WebSocket not available, falling back to standalone simulation", e);
      startFallbackSimulation();
    }
  };

  const handleClear = () => {
    setAgentState({
      status: 'idle',
      agents: [],
      finalResults: null,
      caseId: null,
      error: null
    });
    setComplaintText('');
  }

  return (
    <div className="app-container">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="main-layout">
        {activeTab === 'recommendation' ? (
          <>
            <Sidebar 
              complaintText={complaintText}
              setComplaintText={setComplaintText}
              productType={productType}
              setProductType={setProductType}
              model={model}
              setModel={setModel}
              onRun={handleRunAI}
              isRunning={agentState.status === 'running'}
            />
            <div className="content-area">
              {agentState.status === 'idle' && <LandingView />}
              
              {(agentState.status === 'running' || agentState.status === 'completed' || agentState.status === 'error') && (
                <AgentPanel 
                  agents={agentState.agents} 
                  status={agentState.status} 
                  error={agentState.error} 
                />
              )}
              
              {agentState.status === 'completed' && agentState.finalResults && (
                <>
                  <ResultCards results={agentState.finalResults} />
                  <FeedbackForm caseId={agentState.caseId} />
                  
                  <div style={{ marginTop: '32px', textAlign: 'center' }}>
                    <button 
                      className="btn btn-primary" 
                      style={{ width: 'auto', padding: '12px 32px' }}
                      onClick={() => setAgentState({ status: 'idle', agents: [], caseId: null, finalResults: null })}
                    >
                      + Start New Service Request
                    </button>
                  </div>
                </>
              )}
            </div>
          </>
        ) : (
          <div className="content-area" style={{ padding: '24px' }}>
            <Dashboard />
          </div>
        )}
      </div>
    </div>
  )
}

export default App
