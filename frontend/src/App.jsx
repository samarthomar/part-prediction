import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import AgentPanel from './components/AgentPanel'
import ResultCards from './components/ResultCards'
import FeedbackForm from './components/FeedbackForm'
import Dashboard from './components/Dashboard'
import LandingView from './components/LandingView'
import { getWsUrl } from './apiConfig'
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
    
    // Normally connect to websocket here, but we'll mock it for now
    // if backend isn't available, or implement the real websocket
    try {
      const ws = new WebSocket(getWsUrl());
      
      ws.onopen = () => {
        ws.send(JSON.stringify({
          complaint_text: complaintText,
          product_type: productType,
          model: model
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'started') {
          // pre-populate agents
        } else if (data.type === 'agent_complete') {
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
          setAgentState(prev => ({
            ...prev,
            status: 'error',
            error: data.message
          }));
          ws.close();
        }
      };
      
      ws.onerror = () => {
        setAgentState(prev => ({
          ...prev,
          status: 'error',
          error: 'WebSocket connection failed. Ensure backend is running.'
        }));
      };
    } catch (e) {
      console.error(e);
      setAgentState(prev => ({
        ...prev,
        status: 'error',
        error: e.message
      }));
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
