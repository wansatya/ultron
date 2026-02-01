"""Web tools for fetching and searching"""

import aiohttp
from typing import Dict, Any
from bs4 import BeautifulSoup
from .base import Tool, ToolContext, ToolResult


class WebFetchTool(Tool):
    """Fetch content from a URL"""

    def __init__(self, timeout: int = 10, user_agent: str = "Ultron/1.0"):
        self.timeout = timeout
        self.user_agent = user_agent

    def name(self) -> str:
        return "web.fetch"

    def description(self) -> str:
        return "Fetch content from a URL"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Fetch URL content"""
        valid, error = self.validate_params(params, ["url"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        url = params["url"]

        try:
            headers = {"User-Agent": self.user_agent}

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            output="",
                            error=f"HTTP {response.status}: {response.reason}"
                        )

                    content = await response.text()

                    # Parse HTML if content type is HTML
                    content_type = response.headers.get("Content-Type", "")
                    if "html" in content_type:
                        soup = BeautifulSoup(content, "html.parser")

                        # Remove script and style elements
                        for element in soup(["script", "style"]):
                            element.decompose()

                        # Get text content
                        text = soup.get_text(separator="\n", strip=True)

                        # Remove excessive newlines
                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        text = "\n".join(lines)

                        return ToolResult(
                            success=True,
                            output=text,
                            metadata={
                                "url": url,
                                "content_type": content_type,
                                "size": len(content)
                            }
                        )
                    else:
                        # Return raw content for non-HTML
                        return ToolResult(
                            success=True,
                            output=content,
                            metadata={
                                "url": url,
                                "content_type": content_type,
                                "size": len(content)
                            }
                        )

        except aiohttp.ClientError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to fetch URL: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Unexpected error: {str(e)}"
            )


class WebSearchTool(Tool):
    """Search the web using DuckDuckGo"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def name(self) -> str:
        return "web.search"

    def description(self) -> str:
        return "Search the web for information"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Search the web"""
        valid, error = self.validate_params(params, ["query"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        query = params["query"]

        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params_dict = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params_dict,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            output="",
                            error=f"Search failed with status {response.status}"
                        )

                    data = await response.json()

                    # Extract results
                    results = []

                    # Abstract (instant answer)
                    if data.get("Abstract"):
                        results.append(f"Summary: {data['Abstract']}")
                        if data.get("AbstractURL"):
                            results.append(f"Source: {data['AbstractURL']}")

                    # Related topics
                    if data.get("RelatedTopics"):
                        results.append("\nRelated:")
                        for topic in data["RelatedTopics"][:5]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append(f"- {topic['Text']}")
                                if topic.get("FirstURL"):
                                    results.append(f"  {topic['FirstURL']}")

                    if results:
                        output = "\n".join(results)
                        return ToolResult(
                            success=True,
                            output=output,
                            metadata={"query": query}
                        )
                    else:
                        return ToolResult(
                            success=True,
                            output=f"No instant answers found for '{query}'. Try a web search at: https://duckduckgo.com/?q={query.replace(' ', '+')}",
                            metadata={"query": query}
                        )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Search failed: {str(e)}"
            )
