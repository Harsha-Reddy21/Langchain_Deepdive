import React, { useState, useEffect, useRef } from 'react';
import CodeEditor from './components/CodeEditor';
import OutputPanel from './components/OutputPanel';
import ExplanationPanel from './components/ExplanationPanel';
import Header from './components/Header';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState([]);
  const [explanation, setExplanation] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);
  const [clientId] = useState(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  const { socket, isConnected } = useWebSocket(clientId);
  const outputRef = useRef(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const handleExecuteCode = () => {
    if (!code.trim() || !isConnected) return;
    
    setIsExecuting(true);
    setOutput([]);
    
    socket.send(JSON.stringify({
      type: 'execute_code',
      code: code,
      language: language
    }));
  };

  const handleGetExplanation = () => {
    if (!code.trim() || !isConnected) return;
    
    setIsExplaining(true);
    setExplanation('');
    
    socket.send(JSON.stringify({
      type: 'get_explanation',
      code: code,
      language: language,
      context: 'User wants to understand this code'
    }));
  };

  const handleClearOutput = () => {
    setOutput([]);
    setExplanation('');
  };

  const handleCodeChange = (newCode) => {
    setCode(newCode);
  };

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    setOutput([]);
    setExplanation('');
  };

  // Handle WebSocket messages
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'execution_start':
          setOutput(prev => [...prev, { type: 'info', content: message.message }]);
          break;
          
        case 'execution_result':
          setOutput(prev => [...prev, { type: 'result', content: message.data }]);
          break;
          
        case 'execution_error':
          setOutput(prev => [...prev, { type: 'error', content: message.error }]);
          setIsExecuting(false);
          break;
          
        case 'explanation_result':
          setExplanation(message.explanation);
          setIsExplaining(false);
          break;
          
        case 'explanation_error':
          setExplanation(`Error: ${message.error}`);
          setIsExplaining(false);
          break;
          
        default:
          break;
      }
    };

    socket.addEventListener('message', handleMessage);
    
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket]);

  // Set execution complete when output is received
  useEffect(() => {
    if (output.length > 0 && isExecuting) {
      const lastOutput = output[output.length - 1];
      if (lastOutput.type === 'result' || lastOutput.type === 'error') {
        setIsExecuting(false);
      }
    }
  }, [output, isExecuting]);

  return (
    <div className="app">
      <Header 
        language={language} 
        onLanguageChange={handleLanguageChange}
        isConnected={isConnected}
      />
      
      <div className="main-content">
        <div className="editor-section">
          <CodeEditor
            code={code}
            language={language}
            onChange={handleCodeChange}
            onExecute={handleExecuteCode}
            onExplain={handleGetExplanation}
            isExecuting={isExecuting}
            isExplaining={isExplaining}
            isConnected={isConnected}
          />
        </div>
        
        <div className="panels-section">
          <OutputPanel
            output={output}
            onClear={handleClearOutput}
            ref={outputRef}
          />
          
          <ExplanationPanel
            explanation={explanation}
            isExplaining={isExplaining}
          />
        </div>
      </div>
    </div>
  );
}

export default App; 