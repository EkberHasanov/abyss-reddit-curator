import os
import json
import time
from typing import Dict
from reddit_scraper import get_subreddit_top_posts, RedditScraperError
from service import transform_reddit_posts, ContentGenerationError

def create_output_folder():
    """Create output folder if it doesn't exist."""
    if not os.path.exists('output'):
        os.makedirs('output')

def write_output_file(filename: str, content: str):
    """Write content to a file in the output folder."""
    with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    create_output_folder()
    start_time = time.time()
    
    subreddit = os.environ.get('subreddit', '')
    content_type = os.environ.get('content_type', 'blog_post')
    tone = os.environ.get('tone', 'informative')
    length = os.environ.get('length', 'medium')
    post_limit = int(os.environ.get('post_limit', '5'))
    time_filter = os.environ.get('time_filter', 'day')
    
    if not subreddit:
        error_message = "Error: Subreddit name is required."
        write_output_file('error.txt', error_message)
        return
    
    try:
        posts, subreddit_info = get_subreddit_top_posts(subreddit, limit=post_limit, time_filter=time_filter)
        
        transformed_content = transform_reddit_posts(posts, subreddit_info, content_type, tone, length)
        
        write_output_file('transformed_content.txt', transformed_content)
        
        metadata: Dict[str, str | int | float | Dict[str, str]] = {
            "subreddit": subreddit,
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "posts_analyzed": len(posts),
            "time_filter": time_filter,
            "subreddit_info": subreddit_info,
            "generation_time_seconds": round(time.time() - start_time, 2)
        }
        write_output_file('metadata.json', json.dumps(metadata, indent=2))
        
        summary = f"""
        # Reddit Content Curator - Summary
        
        ## Content Successfully Generated!
        
        Your content has been transformed from r/{subreddit} into a {tone} {content_type}.
        
        ## Details:
        - Subreddit: r/{subreddit} ({subreddit_info['subscribers']} subscribers)
        - Content Type: {content_type}
        - Tone: {tone}
        - Length: {length}
        - Posts Analyzed: {len(posts)}
        - Time Range: {time_filter}
        - Processing Time: {round(time.time() - start_time, 2)} seconds
        
        ## Files Generated:
        - transformed_content.txt: Your main content
        - metadata.json: Details about the generation process
        
        Thank you for using the Reddit Content Curator!
        """
        write_output_file('summary.txt', summary)
        
    except RedditScraperError as e:
        error_message = f"Reddit Error: {str(e)}\n\nPlease check the subreddit name and try again."
        write_output_file('error.txt', error_message)
    
    except ContentGenerationError as e:
        error_message = f"Content Generation Error: {str(e)}\n\nPlease try again with different parameters."
        write_output_file('error.txt', error_message)
    
    except Exception as e:
        error_message = f"Unexpected Error: {str(e)}\n\nPlease try again or contact support."
        write_output_file('error.txt', error_message)

if __name__ == "__main__":
    main()
