from google import genai  # type: ignore
from typing import List, Dict, Any

from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


class ContentGenerationError(Exception):
    """Custom exception for content generation errors."""
    pass

def generate_content(text: str) -> str:
    """Generate content using Gemini API."""
    try:
        response = client.models.generate_content(  # type: ignore
            contents=text,
            model="gemini-2.0-flash-001",
        )
        
        if not hasattr(response, 'text') or not response.text:
            raise ContentGenerationError("No content generated from the model")
        
        return response.text
    except Exception as e:
        raise ContentGenerationError(f"Error generating content: {str(e)}")

def get_content_type_prompt(content_type: str) -> str:
    """Get specific prompt instructions based on content type."""
    content_type_prompts = {
        "youtube_script": """
            Create a YouTube script with:
            1. An attention-grabbing introduction
            2. Clear sections for each main point
            3. Call-to-action at the end
            4. Include [PAUSE] markers where appropriate for the presenter
            Format the script with INTRO, MAIN CONTENT, and OUTRO sections.
        """,
        "instagram_post": """
            Create an Instagram post with:
            1. An engaging caption (max 2200 characters)
            2. Relevant hashtags (10-15)
            3. A call-to-action for engagement
            Format with CAPTION and HASHTAGS sections.
        """,
        "twitter_thread": """
            Create a Twitter thread with:
            1. An attention-grabbing first tweet
            2. 5-8 follow-up tweets that expand on the topic
            3. A concluding tweet with call-to-action
            Format as numbered tweets with (1/X) format.
        """,
        "blog_post": """
            Create a blog post with:
            1. Compelling headline
            2. Introduction that hooks the reader
            3. Subheadings for each major point
            4. Conclusion with key takeaways
            Format with proper HTML tags (<h1>, <h2>, <p>, etc.).
        """,
        "newsletter": """
            Create a newsletter with:
            1. Catchy subject line
            2. Brief introduction
            3. Main content with bullet points for readability
            4. Call-to-action at the end
            Format with SUBJECT LINE, BODY, and FOOTER sections.
        """
    }
    
    default_prompt = """
        Create well-structured content that covers the main points in an engaging way.
        Include an introduction, main points, and conclusion.
    """
    
    return content_type_prompts.get(content_type.lower().replace(" ", "_"), default_prompt)

def get_tone_prompt(tone: str) -> str:
    """Get specific prompt instructions based on tone."""
    tone_prompts = {
        "informative": "Maintain an objective, educational tone. Focus on facts and clear explanations.",
        "humorous": "Use wit, jokes, and playful language. Keep the content light-hearted and entertaining.",
        "professional": "Maintain a formal, business-appropriate tone. Use industry terminology where relevant.",
        "conversational": "Write as if having a friendly conversation. Use casual language and occasionally ask questions.",
        "inspirational": "Use motivational language and storytelling. Focus on possibilities and positive outcomes."
    }
    
    default_prompt = "Write in a balanced, neutral tone that's appropriate for general audiences."
    
    return tone_prompts.get(tone.lower(), default_prompt)

def get_length_guidance(length: str) -> str:
    """Get specific length guidance based on length preference."""
    length_guidance = {
        "short": "Keep the content concise and to-the-point. Aim for about 250-300 words.",
        "medium": "Provide moderate detail. Aim for about 500-700 words.",
        "long": "Offer comprehensive coverage. Aim for about 1000-1500 words."
    }
    
    default_guidance = "Create content of appropriate length for the format, focusing on quality over quantity."
    
    return length_guidance.get(length.lower(), default_guidance)

def transform_reddit_posts(posts: List[Dict[str, Any]], subreddit_info: Dict[str, Any], 
                        content_type: str, tone: str, length: str) -> str:
    """
    Transform Reddit posts into specified content type with given tone and length.
    
    Args:
        posts: List of Reddit post data
        subreddit_info: Information about the subreddit
        content_type: Type of content to generate
        tone: Tone of the content
        length: Length of the content
        
    Returns:
        Transformed content as a string
    """
    try:
        content_type_instructions = get_content_type_prompt(content_type)
        tone_instructions = get_tone_prompt(tone)
        length_instructions = get_length_guidance(length)
        
        posts_summary = "\n\n".join([
            f"Post {i+1}:\nTitle: {post['title']}\nUpvotes: {post['score']}\nComments: {post['num_comments']}\n"
            f"Content: {post['selftext'][:300]}{'...' if len(post['selftext']) > 300 else ''}"
            for i, post in enumerate(posts)
        ])
        
        prompt = f"""
        # Task: Transform Reddit Content

        ## Subreddit Information
        - Name: r/{subreddit_info['name']}
        - Title: {subreddit_info['title']}
        - Description: {subreddit_info['description']}
        - Subscribers: {subreddit_info['subscribers']}

        ## Content Requirements
        - Content Type: {content_type}
        {content_type_instructions}
        
        - Tone: {tone}
        {tone_instructions}
        
        - Length: {length}
        {length_instructions}

        ## Reddit Posts to Transform
        {posts_summary}

        ## Instructions
        1. Create a {content_type} based on these Reddit posts from r/{subreddit_info['name']}
        2. Maintain a {tone} tone throughout
        3. Reference multiple posts to create comprehensive content
        4. Format the content appropriately for the chosen content type
        5. Make the content engaging and valuable to the audience
        """
        
        result = generate_content(prompt)
        return result
    
    except ContentGenerationError:
        raise
    except Exception as e:
        raise ContentGenerationError(f"Error transforming Reddit posts: {str(e)}")
