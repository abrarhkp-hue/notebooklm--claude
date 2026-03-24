import asyncio
from fastmcp import FastMCP
from notebooklm import NotebookLMClient

mcp = FastMCP("NotebookLM")

@mcp.tool()
async def list_notebooks():
    """List all NotebookLM notebooks available in the account."""
    async with await NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()
        return [{"id": nb.id, "title": nb.title} for nb in notebooks]

@mcp.tool()
async def create_notebook(title: str):
    """Create a new NotebookLM notebook."""
    async with await NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create(title)
        return {"id": nb.id, "title": nb.title}

@mcp.tool()
async def add_source_url(notebook_id: str, url: str):
    """Add a web URL source to the NotebookLM notebook."""
    async with await NotebookLMClient.from_storage() as client:
        await client.sources.add_url(notebook_id, url, wait=True)
        return {"status": "success", "url": url}

@mcp.tool()
async def chat_ask(notebook_id: str, message: str):
    """Ask a question to the NotebookLM notebook and get an answer based on its sources."""
    async with await NotebookLMClient.from_storage() as client:
        result = await client.chat.ask(notebook_id, message)
        return {"answer": result.text if hasattr(result, 'text') else result.answer}

if __name__ == "__main__":
    mcp.run()
