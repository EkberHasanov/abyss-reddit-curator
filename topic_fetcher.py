import requests
import json
import random
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ContentFetcherError(Exception):
    pass

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_headers():
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5'
    }

def search_wikipedia(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search Wikipedia for articles related to the given topic."""
    search_url = "https://en.wikipedia.org/w/api.php"
    
    params: Dict[str, str | int] = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": topic,
        "srlimit": limit,
        "srprop": "snippet|titlesnippet|sectiontitle|categorysnippet|score",
        "utf8": 1
    }
    
    try:
        response = requests.get(search_url, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        search_results: List[Dict[str, str | int]] = []
        for result in data.get("query", {}).get("search", []):
            snippet = result.get("snippet", "")
            snippet = snippet.replace("<span class=\"searchmatch\">", "")
            snippet = snippet.replace("</span>", "")
            
            search_results.append({
                "title": result.get("title", ""),
                "pageid": result.get("pageid", 0),
                "snippet": snippet,
                "score": result.get("score", 0),
                "size": result.get("size", 0),
                "wordcount": result.get("wordcount", 0),
                "timestamp": result.get("timestamp", "")
            })
        
        if not search_results:
            raise ContentFetcherError(f"No Wikipedia articles found for topic: {topic}")
        
        return search_results
    
    except requests.exceptions.RequestException as e:
        raise ContentFetcherError(f"Error searching Wikipedia: {str(e)}")
    except json.JSONDecodeError as e:
        raise ContentFetcherError(f"Error parsing Wikipedia search results: {str(e)}")
    except Exception as e:
        raise ContentFetcherError(f"Unexpected error during Wikipedia search: {str(e)}")

def get_article_content(pageid: int) -> Dict[str, Any]:
    """Get the content of a Wikipedia article by page ID."""
    content_url = "https://en.wikipedia.org/w/api.php"
    
    params: Dict[str, str | int] = {
        "action": "query",
        "format": "json",
        "prop": "extracts|categories|links|info|images",
        "pageids": pageid,
        "exintro": 1,
        "explaintext": 1,
        "exsectionformat": "plain",
        "inprop": "url|displaytitle",
        "cllimit": 10,
        "pllimit": 10
    }
    
    try:
        response = requests.get(content_url, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        page_data = data.get("query", {}).get("pages", {}).get(str(pageid), {})
        
        if not page_data or "missing" in page_data:
            raise ContentFetcherError(f"Wikipedia article with page ID {pageid} not found")
        
        article: Dict[str, str | int | List[str]] = {
            "title": page_data.get("title", ""),
            "content": page_data.get("extract", ""),
            "url": page_data.get("fullurl", f"https://en.wikipedia.org/?curid={pageid}"),
            "categories": [cat.get("title", "").replace("Category:", "") for cat in page_data.get("categories", [])],
            "last_modified": page_data.get("touched", ""),
            "pageid": pageid
        }
        
        return article
    
    except requests.exceptions.RequestException as e:
        raise ContentFetcherError(f"Error fetching Wikipedia article: {str(e)}")
    except json.JSONDecodeError as e:
        raise ContentFetcherError(f"Error parsing Wikipedia article data: {str(e)}")
    except Exception as e:
        raise ContentFetcherError(f"Unexpected error fetching Wikipedia article: {str(e)}")

def get_full_article_content(pageid: int) -> Dict[str, Any]:
    """Get the full content of a Wikipedia article by page ID."""
    content_url = "https://en.wikipedia.org/w/api.php"
    
    params: Dict[str, str | int] = {
        "action": "query",
        "format": "json",
        "prop": "extracts|categories|links|info|images",
        "pageids": pageid,
        "explaintext": 1,
        "exsectionformat": "plain",
        "inprop": "url|displaytitle",
        "cllimit": 10,
        "pllimit": 10
    }
    
    try:
        response = requests.get(content_url, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        page_data = data.get("query", {}).get("pages", {}).get(str(pageid), {})
        
        if not page_data or "missing" in page_data:
            raise ContentFetcherError(f"Wikipedia article with page ID {pageid} not found")
        
        full_content = page_data.get("extract", "")
        
        if len(full_content) > 10000:
            full_content = full_content[:10000] + "... [content truncated]"
        
        article: Dict[str, str | int | List[str]] = {
            "title": page_data.get("title", ""),
            "content": full_content,
            "url": page_data.get("fullurl", f"https://en.wikipedia.org/?curid={pageid}"),
            "categories": [cat.get("title", "").replace("Category:", "") for cat in page_data.get("categories", [])],
            "last_modified": page_data.get("touched", ""),
            "pageid": pageid
        }
        
        return article
    
    except requests.exceptions.RequestException as e:
        raise ContentFetcherError(f"Error fetching full Wikipedia article: {str(e)}")
    except json.JSONDecodeError as e:
        raise ContentFetcherError(f"Error parsing full Wikipedia article data: {str(e)}")
    except Exception as e:
        raise ContentFetcherError(f"Unexpected error fetching full Wikipedia article: {str(e)}")

def get_related_articles(pageid: int, limit: int = 3) -> List[Dict[str, Any]]:
    """Get related Wikipedia articles based on links within the given article."""
    links_url = "https://en.wikipedia.org/w/api.php"
    
    params: Dict[str, str | int] = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "pageids": pageid,
        "pllimit": 30
    }
    
    try:
        response = requests.get(links_url, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        page_data = data.get("query", {}).get("pages", {}).get(str(pageid), {})
        
        links = page_data.get("links", [])
        
        filtered_links: List[str] = []
        for link in links:
            title = link.get("title", "")
            if ":" not in title and "Wikipedia" not in title and "Template" not in title and "Category" not in title:
                filtered_links.append(title)
        
        relevant_links = filtered_links[:limit]
        
        related_articles: List[Dict[str, Any]] = []
        for title in relevant_links:
            try:
                search_result = search_wikipedia(f'intitle:"{title}"', limit=1)
                if search_result:
                    pageid = search_result[0].get("pageid", 0)
                    article_data = get_article_content(pageid)
                    related_articles.append(article_data)
                    time.sleep(0.5)
            except:
                continue
        
        return related_articles
    
    except requests.exceptions.RequestException as e:
        raise ContentFetcherError(f"Error fetching related articles: {str(e)}")
    except json.JSONDecodeError as e:
        raise ContentFetcherError(f"Error parsing related articles data: {str(e)}")
    except Exception as e:
        raise ContentFetcherError(f"Unexpected error fetching related articles: {str(e)}")

def get_topic_content(topic: str, num_articles: int = 3, include_related: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Get comprehensive content about a topic from Wikipedia.
    
    Args:
        topic: The topic to search for
        num_articles: Number of main articles to fetch 
        include_related: Whether to fetch related articles
        
    Returns:
        Tuple of (list of article dictionaries, topic metadata dictionary)
    """
    try:
        search_results = search_wikipedia(topic, limit=num_articles + 2)
        
        topic_info: Dict[str, str | int] = {
            "topic": topic,
            "search_term": topic,
            "num_results": len(search_results),
            "timestamp": datetime.now().isoformat()
        }
        
        articles: List[Dict[str, Any]] = []
        for i, result in enumerate(search_results[:num_articles]):
            pageid = result.get("pageid")
            
            assert pageid is not None
            if i == 0:
                article = get_full_article_content(pageid)
            else:
                article = get_article_content(pageid)
            
            if i == 0 and include_related:
                article["related_articles"] = get_related_articles(pageid)
            
            articles.append(article)
            
            time.sleep(0.5)
        
        return articles, topic_info
        
    except ContentFetcherError:
        raise
    except Exception as e:
        raise ContentFetcherError(f"Error fetching topic content: {str(e)}")
