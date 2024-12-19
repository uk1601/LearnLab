from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
import arxiv
from urllib.parse import quote_plus

@tool("WebSearch")
async def web_search(query: str) -> List[Dict[str, str]]:
    """Searches web for relevant information.
    Args:
        query (str): Search query
    Returns:
        List[Dict]: List of search results with title, link, and snippet
    """
    try:
        search = DuckDuckGoSearchResults()
        raw_results = search.run(query)
        
        results = []
        current_result = {}
        
        for line in raw_results.split('\n'):
            if line.startswith('title: '):
                if current_result:
                    results.append(current_result.copy())
                current_result = {'title': line[7:]}
            elif line.startswith('link: '):
                current_result['link'] = line[6:]
            elif line.startswith('snippet: '):
                current_result['snippet'] = line[9:]
        
        if current_result:
            results.append(current_result.copy())
            
        return results

    except Exception as e:
        print(f"Web search error: {str(e)}")
        return []

@tool("ArXiv")
async def arxiv_search(query: str) -> List[Dict[str, Any]]:
    """Fetches academic papers from arXiv.
    Args:
        query (str): Search query for papers
    Returns:
        List[Dict]: List of papers with title, authors, abstract, and url
    """
    try:
        # Clean query
        sanitized_query = quote_plus(query.strip())
        
        # Search arxiv
        search = arxiv.Search(
            query=sanitized_query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "authors": [str(author) for author in paper.authors],
                "abstract": paper.summary,
                "url": paper.pdf_url,
                "published": paper.published.isoformat() if paper.published else None
            })
            
        return results
        
    except Exception as e:
        print(f"ArXiv search error: {str(e)}")
        return []