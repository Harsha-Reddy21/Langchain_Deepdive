import React from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

function CodeEditor({
  code,
  language,
  onChange,
  onExecute,
  onExplain,
  isExecuting,
  isExplaining,
  isConnected
}) {
  const handleEditorChange = (value) => {
    onChange(value || '');
  };

  const getLanguageMode = (lang) => {
    switch (lang.toLowerCase()) {
      case 'python':
        return 'python';
      case 'javascript':
      case 'js':
        return 'javascript';
      default:
        return 'plaintext';
    }
  };

  const getSampleCode = (lang) => {
    switch (lang.toLowerCase()) {
      case 'python':
        return `# Welcome to Smart Code Tutor!
# Try this sample Python code:

def fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"Fibonacci({i}) = {fibonacci(i)}")

# List comprehension example
squares = [x**2 for x in range(5)]
print(f"Squares: {squares}")`;
      
      case 'javascript':
        return `// Welcome to Smart Code Tutor!
// Try this sample JavaScript code:

function fibonacci(n) {
    // Calculate the nth Fibonacci number
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

// Test the function
for (let i = 0; i < 10; i++) {
    console.log(\`Fibonacci(\${i}) = \${fibonacci(i)}\`);
}

// Array methods example
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
console.log(\`Doubled: \${doubled}\`);`;
      
      default:
        return '';
    }
  };

  const handleLoadSample = () => {
    onChange(getSampleCode(language));
  };

  return (
    <div className="code-editor">
      <div className="editor-header">
        <div className="editor-title">
          <span className="editor-icon">📝</span>
          Code Editor
        </div>
        <div className="editor-actions">
          <button
            className="btn btn-secondary"
            onClick={handleLoadSample}
            disabled={!isConnected}
          >
            Load Sample
          </button>
          <button
            className="btn btn-primary"
            onClick={onExecute}
            disabled={!isConnected || isExecuting || !code.trim()}
          >
            {isExecuting ? (
              <>
                <span className="spinner"></span>
                Executing...
              </>
            ) : (
              <>
                <span>▶️</span>
                Run Code
              </>
            )}
          </button>
          <button
            className="btn btn-secondary"
            onClick={onExplain}
            disabled={!isConnected || isExplaining || !code.trim()}
          >
            {isExplaining ? (
              <>
                <span className="spinner"></span>
                Explaining...
              </>
            ) : (
              <>
                <span>🤖</span>
                Explain
              </>
            )}
          </button>
        </div>
      </div>
      
      <div className="editor-container">
        <Editor
          height="100%"
          language={getLanguageMode(language)}
          value={code}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            wordWrap: 'on',
            folding: true,
            lineDecorationsWidth: 10,
            lineNumbersMinChars: 3,
            glyphMargin: false,
            contextmenu: true,
            quickSuggestions: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnEnter: 'on',
            tabCompletion: 'on',
            wordBasedSuggestions: true,
            parameterHints: {
              enabled: true
            }
          }}
        />
      </div>
    </div>
  );
}

export default CodeEditor; 