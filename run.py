import os
import json
import time
from typing import Any, Dict
from topic_fetcher import get_topic_content, ContentFetcherError
from service import transform_topic_content, ContentGenerationError


def create_output_folder():

    if not os.path.exists('output'):
        os.makedirs('output')


def write_output_file(filename: str, content: str):

    with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    create_output_folder()
    start_time = time.time()
    
    topic = os.environ.get('topic', '').strip()
    content_type = os.environ.get('content_type', 'blog_post')
    tone = os.environ.get('tone', 'informative')
    length = os.environ.get('length', 'medium')
    num_articles = int(os.environ.get('num_articles', '3'))

    if not topic:
        write_output_file('error.txt', "Error: Topic is required.")
        return
    
    try:
        write_output_file('status.txt', f"⏳ Researching information about '{topic}'...")
        
        articles, topic_info = get_topic_content(topic, num_articles=num_articles)
        
        write_output_file('status.txt', f"✅ Found {len(articles)} articles about '{topic}'!\n⏳ Now transforming into {tone} {content_type}...")
        
        transformed_content = transform_topic_content(articles, topic_info, content_type, tone, length)
        
        write_output_file('transformed_content.html', transformed_content)
        
        metadata: Dict[str, Any] = {
            "topic": topic,
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "articles_analyzed": len(articles),
            "main_article": articles[0]["title"] if articles else "",
            "main_article_url": articles[0]["url"] if articles else "",
            "generation_time_seconds": round(time.time() - start_time, 2)
        }
        write_output_file('metadata.json', json.dumps(metadata, indent=2))
        
        summary = f"""
        # 🎉 Your Content is Ready!
        
        ## ✨ Content Successfully Generated
        
        We've created {tone} {content_type} about "{topic}".
        
        ## 📊 Details:
        - Topic: {topic}
        - Content Type: {content_type}
        - Tone: {tone}
        - Length: {length}
        - Articles Analyzed: {len(articles)}
        - Main Source: {articles[0]["title"] if articles else ""}
        - Processing Time: {round(time.time() - start_time, 2)} seconds
        
        ## 📄 Files Generated:
        - transformed_content.txt: Your main content
        - metadata.json: Details about the generation process
        
        ## 🚀 Next Steps:
        1. Copy your content from transformed_content.txt
        2. Use it on your preferred platform
        3. Enjoy the engagement from your audience!
        
        Thank you for using the Content Alchemist!
        """
        write_output_file('summary.txt', summary)
        
    except ContentFetcherError as e:
        error_message = f"Research Error: {str(e)}\n\nPlease try a different topic or check your spelling."
        write_output_file('error.txt', error_message)
    
    except ContentGenerationError as e:
        error_message = f"Content Generation Error: {str(e)}\n\nPlease try again with different parameters."
        write_output_file('error.txt', error_message)
    
    except Exception as e:
        error_message = f"Unexpected Error: {str(e)}\n\nPlease try again or contact support."
        write_output_file('error.txt', error_message)

if __name__ == "__main__":
    main()
