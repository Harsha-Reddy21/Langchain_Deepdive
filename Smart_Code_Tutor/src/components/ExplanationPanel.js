import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './ExplanationPanel.css';

function ExplanationPanel({ explanation, isExplaining }) {
  const formatExplanation = (text) => {
    if (!text) return '';
    
    // Split by numbered points and format them
    const lines = text.split('\n');
    const formattedLines = lines.map((line, index) => {
      // Check for numbered points (1., 2., etc.)
      if (/^\d+\./.test(line.trim())) {
        return `<div class="explanation-point">${line}</div>`;
      }
      // Check for headers (lines that end with :)
      if (line.trim().endsWith(':') && line.trim().length < 50) {
        return `<div class="explanation-header">${line}</div>`;
      }
      return line;
    });
    
    return formattedLines.join('\n');
  };

  const renderExplanation = () => {
    if (!explanation) return null;
    
    const formattedText = formatExplanation(explanation);
    
    // Split by HTML-like tags we added
    const parts = formattedText.split(/(<div class="explanation-[^"]*">[^<]*<\/div>)/);
    
    return parts.map((part, index) => {
      if (part.startsWith('<div class="explanation-point">')) {
        const content = part.replace(/<div class="explanation-point">([^<]*)<\/div>/, '$1');
        return (
          <div key={index} className="explanation-point">
            {content}
          </div>
        );
      }
      if (part.startsWith('<div class="explanation-header">')) {
        const content = part.replace(/<div class="explanation-header">([^<]*)<\/div>/, '$1');
        return (
          <div key={index} className="explanation-header">
            {content}
          </div>
        );
      }
      if (part.trim()) {
        return (
          <div key={index} className="explanation-text">
            {part}
          </div>
        );
      }
      return null;
    });
  };

  return (
    <div className="explanation-panel card">
      <div className="explanation-header">
        <div className="explanation-title">
          <span className="explanation-icon">🤖</span>
          AI Explanation
        </div>
        {isExplaining && (
          <div className="explanation-status">
            <span className="spinner"></span>
            Analyzing...
          </div>
        )}
      </div>
      
      <div className="explanation-content">
        {!explanation && !isExplaining ? (
          <div className="explanation-empty">
            <span className="empty-icon">💡</span>
            <p>Click "Explain" to get AI-powered insights about your code!</p>
            <small>Get step-by-step explanations, best practices, and improvement suggestions.</small>
          </div>
        ) : isExplaining ? (
          <div className="explanation-loading">
            <div className="loading-content">
              <span className="spinner"></span>
              <p>Analyzing your code...</p>
              <small>Retrieving relevant documentation and generating explanations.</small>
            </div>
          </div>
        ) : (
          <div className="explanation-text-content">
            {renderExplanation()}
          </div>
        )}
      </div>
    </div>
  );
}

export default ExplanationPanel; 