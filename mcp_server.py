import ast
import operator
from typing import Dict, Any, List
from rag_pipeline import query_vector_store

# Gracefully import DDGS
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# Try SDK FastMCP first, fallback to standalone fastmcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

# Instantiate standalone MCP Server
mcp = FastMCP("EngineeringToolsServer")

# --- Safe AST Math Logic ---
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are supported.")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](_eval_node(node.left), _eval_node(node.right))
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](_eval_node(node.operand))
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    else:
        raise ValueError(f"Unsupported expression construct: {type(node).__name__}")


@mcp.tool()
def evaluate_math_expression(expression: str) -> Dict[str, Any]:
    """
    Evaluates exact mathematical, algebraic, or engineering arithmetic expressions.
    Use this whenever calculations or precise formulas are needed.
    """
    try:
        cleaned = expression.strip()
        parsed = ast.parse(cleaned, mode="eval")
        result = _eval_node(parsed.body)
        return {"expression": cleaned, "result": result, "status": "success"}
    except Exception as e:
        return {"expression": expression, "error": str(e), "status": "failed"}


@mcp.tool()
def web_search(query: str, max_results: int = 4) -> Dict[str, Any]:
    """
    Searches the live internet for recent documentation, real-time events, pinouts, or technical errata.
    """
    try:
        cleaned_query = query.strip().strip('"').strip("'")
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(cleaned_query, max_results=max_results))
            if not raw_results:
                return {"query": cleaned_query, "results": [], "status": "empty"}
            formatted_results = [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                }
                for r in raw_results
            ]
            return {"query": cleaned_query, "results": formatted_results, "status": "success"}
    except Exception as e:
        return {"query": query, "error": str(e), "status": "failed"}


if __name__ == "__main__":
    # Runs the server over stdio transport
    mcp.run()

@mcp.tool() # (or @mcp.tool() if pinned to mcp<2)
def query_knowledge_base(query: str, top_k: int = 2) -> Dict[str, Any]:
    """
    Searches internal technical documents, datasheets, and guides for specifications and operational limits.
    Use this whenever answering questions about hardware ratings, component datasheets, or system architecture.
    """
    try:
        chunks = query_vector_store(query_text=query, top_k=top_k)
        return {
            "query": query,
            "matched_chunks": chunks,
            "status": "success" if chunks else "no_matches"
        }
    except Exception as e:
        return {"query": query, "error": str(e), "status": "failed"}