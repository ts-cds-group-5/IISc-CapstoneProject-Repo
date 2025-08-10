from fastmcp import FastMCP

# Initialize FastMCP with the specified configuration
mcp = FastMCP(name="tserver")
    
def main():
    if __name__ == "__main__":
        mcp.run(transport="stdio")

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b