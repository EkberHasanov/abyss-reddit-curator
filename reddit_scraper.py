import requests
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

class RedditScraperError(Exception):
    """Custom exception for Reddit scraper errors."""
    pass

def fetch_subreddit_info(subreddit_name: str) -> Dict[str, str]:
    """
    Fetch information about a subreddit using Reddit's JSON API.
    
    Args:
        subreddit_name: Name of the subreddit
        
    Returns:
        Dictionary with subreddit information
    """
    url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
    headers = {
        'User-Agent': 'ContentCurator/1.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 404:
            raise RedditScraperError(f"Subreddit r/{subreddit_name} not found")
        
        response.raise_for_status()
        
        data = response.json()
        
        subreddit_data = data.get('data', {})
        return {
            'name': subreddit_data.get('display_name', subreddit_name),
            'title': subreddit_data.get('title', ''),
            'description': subreddit_data.get('public_description', ''),
            'subscribers': subreddit_data.get('subscribers', 0),
            'created_utc': subreddit_data.get('created_utc', 0),
            'over18': subreddit_data.get('over18', False),
            'url': f"https://www.reddit.com/r/{subreddit_name}/"
        }
    except requests.exceptions.RequestException as e:
        raise RedditScraperError(f"Error fetching subreddit information: {str(e)}")
    except (json.JSONDecodeError, ValueError) as e:
        raise RedditScraperError(f"Error parsing subreddit data: {str(e)}")
    except Exception as e:
        raise RedditScraperError(f"Unexpected error fetching subreddit info: {str(e)}")

def get_subreddit_top_posts(subreddit_name: str, limit: int = 5, time_filter: str = 'day') -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Fetch top posts from a subreddit using Reddit's JSON API.
    
    Args:
        subreddit_name: Name of the subreddit to fetch posts from
        limit: Maximum number of posts to fetch
        time_filter: Time filter for posts (day, week, month, year, all)
        
    Returns:
        Tuple of (list of post dictionaries, subreddit info dictionary)
    """
    try:
        valid_time_filters = ['day', 'week', 'month', 'year', 'all']
        if time_filter not in valid_time_filters:
            raise RedditScraperError(f"Invalid time filter: {time_filter}. Valid options are: {', '.join(valid_time_filters)}")
        
        subreddit_info = fetch_subreddit_info(subreddit_name)
        
        url = f"https://www.reddit.com/r/{subreddit_name}/top.json?t={time_filter}&limit={limit}"
        headers = {
            'User-Agent': 'ContentCurator/1.0'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RedditScraperError(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
        except json.JSONDecodeError as e:
            raise RedditScraperError(f"Error parsing Reddit data: {str(e)}")
        
        posts: List[Dict[str, str]] = []
        for post_data in data.get('data', {}).get('children', []):
            post = post_data.get('data', {})
            
            selftext = post.get('selftext', '')
            if not selftext and post.get('is_self', False):
                selftext = "[No text content available]"
            
            if len(selftext) > 2000:
                selftext = selftext[:2000] + "... [truncated]"
            
            post_info: Dict[str, str] = {
                'title': post.get('title', ''),
                'score': post.get('score', 0),
                'url': post.get('url', ''),
                'selftext': selftext,
                'num_comments': post.get('num_comments', 0),
                'created_utc': post.get('created_utc', 0),
                'permalink': f"https://www.reddit.com{post.get('permalink', '')}",
                'is_self': post.get('is_self', False),
                'subreddit': subreddit_name,
                'author': post.get('author', '[deleted]'),
                'created_formatted': datetime.fromtimestamp(post.get('created_utc', 0), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            posts.append(post_info)
        
        if not posts:
            raise RedditScraperError(f"No posts found in r/{subreddit_name} with time filter '{time_filter}'")
        
        return posts, subreddit_info
    
    except RedditScraperError:
        raise
    except Exception as e:
        raise RedditScraperError(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
