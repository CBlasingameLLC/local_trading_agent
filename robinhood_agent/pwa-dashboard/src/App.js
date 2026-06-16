import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Activity, CheckCircle, XCircle } from 'lucide-react';

export default function App() {
  const [logs, setLogs] = useState([]);
  const [pendingTrades, setPendingTrades] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    // Connect to the local Python FastAPI server
    // Dynamically use secure wss:// if on Cloudflare, or ws:// if on local Wi-Fi
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/agent`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      setLogs((prev) => [...prev, data.message]);

      // If the Python backend pauses for manual approval, pop it into the UI queue
      if (data.type === "awaiting_approval") {
        setPendingTrades((prev) => [...prev, data]);
      }
    };

    return () => {
      ws.current.close();
    };
  }, []);

  const handleAction = (action, trade) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        command: action,
        ticker: trade.ticker,
        limit_price: trade.limit_price,
        quantity: trade.quantity
      }));
      // Remove from UI queue
      setPendingTrades((prev) => prev.filter(t => t.ticker !== trade.ticker));
    }
  };

  const fireKillSwitch = () => {
    if (ws.current) {
      ws.current.send(JSON.stringify({ command: "KILL_SWITCH" }));
      alert("KILL SIGNAL SENT TO PYTHON BACKEND");
    }
  };

  return (
    <div style={{ backgroundColor: '#111827', color: '#fff', minHeight: '100vh', padding: '20px', fontFamily: 'monospace' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #374151', paddingBottom: '10px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.25rem' }}>
          <Activity color={isConnected ? "#10B981" : "#EF4444"} />
          Agentic Dashboard
        </h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => ws.current && ws.current.send(JSON.stringify({ command: "FORCE_SCAN" }))}
            style={{ backgroundColor: '#3B82F6', color: 'white', padding: '10px 20px', borderRadius: '5px', fontWeight: 'bold', border: 'none', cursor: 'pointer' }}>
            ⚡ FORCE SCAN
          </button>
          <button 
            onClick={fireKillSwitch}
            style={{ backgroundColor: '#EF4444', color: 'white', padding: '10px 20px', borderRadius: '5px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px', border: 'none', cursor: 'pointer' }}>
            <ShieldAlert size={20} />
            KILL SWITCH
          </button>
        </div>
      </div>

      {/* Manual Approval Queue */}
      {pendingTrades.length > 0 && (
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#1F2937', borderRadius: '8px', borderLeft: '4px solid #F59E0B' }}>
          <h2 style={{ color: '#F59E0B', marginTop: 0 }}>Action Required: Pending Trades</h2>
          {pendingTrades.map((trade, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#374151', padding: '10px', borderRadius: '5px', marginTop: '10px' }}>
              <span>Buy <strong>{trade.quantity}x {trade.ticker}</strong> @ ${trade.limit_price}</span>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={() => handleAction("APPROVE_TRADE", trade)} style={{ backgroundColor: '#10B981', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <CheckCircle size={16} /> Approve
                </button>
                <button onClick={() => handleAction("REJECT_TRADE", trade)} style={{ backgroundColor: '#4B5563', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <XCircle size={16} /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Terminal Output */}
      <div style={{ backgroundColor: '#000', padding: '15px', borderRadius: '8px', height: '400px', overflowY: 'auto', border: '1px solid #374151' }}>
        <div style={{ color: '#10B981', marginBottom: '10px' }}>user@agent-core:~$ streaming logs...</div>
        {logs.map((log, i) => (
          <div key={i} style={{ marginBottom: '4px' }}>{log}</div>
        ))}
      </div>
    </div>
  );
}