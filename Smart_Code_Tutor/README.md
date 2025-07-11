# Smart Code Tutor 🚀

A full-stack interactive code interpreter with AI-powered explanations, featuring real-time code execution and intelligent documentation retrieval.

## Features

- **🖥️ Interactive Code Editor**: Monaco editor with syntax highlighting for Python and JavaScript
- **⚡ Real-time Execution**: Execute code in secure E2B sandbox with live streaming output
- **🤖 AI-Powered Explanations**: Get intelligent code explanations using LangChain RAG system
- **📡 WebSocket Streaming**: Real-time communication between frontend and backend
- **🎨 Modern UI**: Beautiful, responsive design with dark theme
- **🔒 Secure Execution**: Sandboxed code execution environment
- **📚 Documentation Retrieval**: Context-aware coding best practices and error solutions

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time bidirectional communication
- **LangChain**: AI/LLM integration and RAG system
- **E2B**: Secure code execution sandbox
- **FAISS**: Vector database for documentation retrieval

### Frontend
- **React**: Modern UI framework
- **Monaco Editor**: Professional code editor
- **WebSocket Client**: Real-time communication
- **Advanced CSS**: Modern styling with CSS variables
- **Responsive Design**: Mobile-friendly interface

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- E2B API key
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Smart_Code_Tutor
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   E2B_API_KEY=your_e2b_api_key_here
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   npm install
   ```

## Running the Application

### Development Mode

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server**
   ```bash
   npm start
   ```

3. **Open your browser**
   Navigate to `http://localhost:3000`

### Production Mode

1. **Build the frontend**
   ```bash
   npm run build
   ```

2. **Start the production server**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Usage

1. **Select Language**: Choose between Python or JavaScript from the dropdown
2. **Write Code**: Use the Monaco editor to write your code
3. **Load Sample**: Click "Load Sample" to get example code
4. **Execute**: Click "Run Code" to execute your code in the sandbox
5. **Get Explanation**: Click "Explain" to get AI-powered code analysis
6. **View Results**: See real-time output and explanations in the side panels

## API Endpoints

- `GET /`: Health check endpoint
- `WebSocket /ws/{client_id}`: Real-time communication endpoint

## WebSocket Message Types

### Client to Server
- `execute_code`: Execute code in sandbox
- `get_explanation`: Get AI explanation for code

### Server to Client
- `execution_start`: Code execution started
- `execution_result`: Code execution result
- `execution_error`: Code execution error
- `explanation_result`: AI explanation result
- `explanation_error`: AI explanation error

## Project Structure

```
Smart_Code_Tutor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── websocket_manager.py # WebSocket connection manager
│   ├── code_executor.py     # E2B code execution
│   ├── rag_system.py        # LangChain RAG system
│   └── __init__.py
├── src/
│   ├── components/
│   │   ├── Header.js        # Application header
│   │   ├── CodeEditor.js    # Monaco editor component
│   │   ├── OutputPanel.js   # Execution output display
│   │   └── ExplanationPanel.js # AI explanation display
│   ├── hooks/
│   │   └── useWebSocket.js  # WebSocket hook
│   ├── App.js              # Main application component
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── public/
│   └── index.html          # HTML template
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LangChain
- `E2B_API_KEY`: Your E2B API key for sandbox execution
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: True)

### Customization

- **Add Languages**: Extend `code_executor.py` and frontend language selector
- **Custom Documentation**: Modify `rag_system.py` to include your own documentation
- **UI Themes**: Update CSS variables in `src/index.css`
- **Editor Settings**: Modify Monaco editor options in `CodeEditor.js`

## Security Features

- **Sandboxed Execution**: All code runs in isolated E2B environment
- **Input Validation**: Server-side validation of all inputs
- **CORS Protection**: Configured CORS middleware
- **Error Handling**: Comprehensive error handling and logging

## Performance Features

- **Concurrent Execution**: Handle multiple code executions simultaneously
- **Streaming Responses**: Real-time output streaming
- **Connection Management**: Automatic WebSocket reconnection
- **Caching**: Vector database caching for documentation retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code examples

## Roadmap

- [ ] Support for more programming languages
- [ ] Advanced code analysis features
- [ ] Collaborative coding sessions
- [ ] Code snippet sharing
- [ ] Integration with version control systems
- [ ] Mobile app development 