import React, { forwardRef } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './OutputPanel.css';

const OutputPanel = forwardRef(({ output, onClear }, ref) => {
  const formatOutput = (item) => {
    if (typeof item.content === 'object') {
      return JSON.stringify(item.content, null, 2);
    }
    return String(item.content);
  };

  const getOutputTypeIcon = (type) => {
    switch (type) {
      case 'info':
        return 'ℹ️';
      case 'result':
        return '✅';
      case 'error':
        return '❌';
      case 'output':
        return '📤';
      default:
        return '📄';
    }
  };

  const getOutputTypeClass = (type) => {
    switch (type) {
      case 'info':
        return 'output-info';
      case 'result':
        return 'output-result';
      case 'error':
        return 'output-error';
      case 'output':
        return 'output-stdout';
      default:
        return 'output-default';
    }
  };

  const getLanguage = (content) => {
    if (typeof content === 'object') {
      return 'json';
    }
    // Try to detect language from content
    const text = String(content);
    if (text.includes('{') && text.includes('}')) {
      return 'json';
    }
    if (text.includes('[') && text.includes(']')) {
      return 'json';
    }
    return 'text';
  };

  return (
    <div className="output-panel card">
      <div className="output-header">
        <div className="output-title">
          <span className="output-icon">📊</span>
          Execution Output
        </div>
        <button
          className="btn btn-secondary"
          onClick={onClear}
          disabled={output.length === 0}
        >
          Clear
        </button>
      </div>
      
      <div className="output-content" ref={ref}>
        {output.length === 0 ? (
          <div className="output-empty">
            <span className="empty-icon">🚀</span>
            <p>Run your code to see the output here!</p>
            <small>Results will appear in real-time as your code executes.</small>
          </div>
        ) : (
          <div className="output-list">
            {output.map((item, index) => (
              <div
                key={index}
                className={`output-item ${getOutputTypeClass(item.type)}`}
              >
                <div className="output-item-header">
                  <span className="output-type-icon">
                    {getOutputTypeIcon(item.type)}
                  </span>
                  <span className="output-type-label">
                    {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
                  </span>
                  {item.output_type && (
                    <span className="output-stream">
                      {item.output_type}
                    </span>
                  )}
                </div>
                
                <div className="output-item-content">
                  {item.type === 'error' ? (
                    <SyntaxHighlighter
                      language="text"
                      style={tomorrow}
                      customStyle={{
                        margin: 0,
                        padding: '0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.2)'
                      }}
                    >
                      {formatOutput(item)}
                    </SyntaxHighlighter>
                  ) : (
                    <SyntaxHighlighter
                      language={getLanguage(item.content)}
                      style={tomorrow}
                      customStyle={{
                        margin: 0,
                        padding: '0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        backgroundColor: 'var(--background-dark)',
                        border: '1px solid var(--border-color)'
                      }}
                    >
                      {formatOutput(item)}
                    </SyntaxHighlighter>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
});

OutputPanel.displayName = 'OutputPanel';

export default OutputPanel; 