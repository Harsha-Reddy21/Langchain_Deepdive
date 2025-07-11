import asyncio
import json
import os
from typing import AsyncGenerator
from e2b import Sandbox
from dotenv import load_dotenv

load_dotenv()

e2b_sandbox = None

async def get_e2b_sandbox():
    global e2b_sandbox
    if e2b_sandbox is None:
        e2b_sandbox = Sandbox(template="base", api_key=os.getenv("E2B_API_KEY"))
    return e2b_sandbox

async def execute_code(code: str, language: str) -> AsyncGenerator[dict, None]:
    """Execute code in E2B sandbox and yield results as they come"""
    
    sandbox = await get_e2b_sandbox()
    
    try:
        if language.lower() == "python":
            async for result in execute_python_code(sandbox, code):
                yield result
        elif language.lower() in ["javascript", "js"]:
            async for result in execute_javascript_code(sandbox, code):
                yield result
        else:
            yield {"type": "error", "message": f"Unsupported language: {language}"}
            
    except Exception as e:
        yield {"type": "error", "message": str(e)}

async def execute_python_code(sandbox: Sandbox, code: str) -> AsyncGenerator[dict, None]:
    """Execute Python code and stream results"""
    try:
        result = await sandbox.run(cmd=["python", "-c", code])
        if result.stdout:
            yield {"type": "result", "content": result.stdout}
        if result.stderr:
            yield {"type": "error", "content": result.stderr}
        if not result.stdout and not result.stderr:
            yield {"type": "result", "content": "Execution completed successfully"}
    except Exception as e:
        yield {"type": "error", "content": str(e)}

async def execute_javascript_code(sandbox: Sandbox, code: str) -> AsyncGenerator[dict, None]:
    """Execute JavaScript code and stream results"""
    try:
        # Write code to a temporary file in the sandbox
        file_path = "/tmp/code.js"
        await sandbox.filesystem.write(file_path, code)
        result = await sandbox.run(cmd=["node", file_path])
        if result.stdout:
            yield {"type": "result", "content": result.stdout}
        if result.stderr:
            yield {"type": "error", "content": result.stderr}
        if not result.stdout and not result.stderr:
            yield {"type": "result", "content": "Execution completed successfully"}
    except Exception as e:
        yield {"type": "error", "content": str(e)}

async def cleanup_sandbox():
    """Cleanup E2B sandbox"""
    global e2b_sandbox
    if e2b_sandbox:
        await e2b_sandbox.close()
        e2b_sandbox = None 