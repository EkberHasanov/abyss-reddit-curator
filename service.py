from google import genai  # type: ignore
from typing import List, Dict, Any

from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


class ContentGenerationError(Exception):

    pass


def generate_content(text: str) -> str:

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

    length_guidance = {
        "short": "Keep the content concise and to-the-point. Aim for about 250-300 words.",
        "medium": "Provide moderate detail. Aim for about 500-700 words.",
        "long": "Offer comprehensive coverage. Aim for about 1000-1500 words."
    }
    
    default_guidance = "Create content of appropriate length for the format, focusing on quality over quantity."
    
    return length_guidance.get(length.lower(), default_guidance)

def transform_topic_content(articles: List[Dict[str, Any]], topic_info: Dict[str, Any], 
                        content_type: str, tone: str, length: str) -> str:

    try:
        content_type_instructions = get_content_type_prompt(content_type)
        tone_instructions = get_tone_prompt(tone)
        length_instructions = get_length_guidance(length)
        
        main_article = articles[0] if articles else {}
        main_content = main_article.get("content", "")
        main_title = main_article.get("title", "")
        categories = main_article.get("categories", [])
        
        related_articles_content = ""
        related_articles = main_article.get("related_articles", [])
        
        if related_articles:
            related_articles_content = "\n\n## Related Topics\n"
            for i, article in enumerate(related_articles):
                related_articles_content += f"\n### {i+1}. {article.get('title', '')}\n"
                related_articles_content += f"{article.get('content', '')[:300]}...\n"
        
        additional_articles_content = ""
        if len(articles) > 1:
            additional_articles_content = "\n\n## Additional Information\n"
            for i, article in enumerate(articles[1:]):
                additional_articles_content += f"\n### {i+1}. {article.get('title', '')}\n"
                additional_articles_content += f"{article.get('content', '')[:300]}...\n"
        
        prompt = f"""
        # Task: Transform Wikipedia Content into {content_type}

        ## Topic Information
        - Main Topic: {topic_info['topic']}
        - Main Article: {main_title}

        ## Content Requirements
        - Content Type: {content_type}
        {content_type_instructions}
        
        - Tone: {tone}
        {tone_instructions}
        
        - Length: {length}
        {length_instructions}

        ## Main Content
        {main_content}

        {related_articles_content}
        
        {additional_articles_content}

        ## Content Categories
        {', '.join(categories)}

        ## Instructions
        1. Create a {content_type} about "{topic_info['topic']}" using the provided information
        2. Maintain a {tone} tone throughout
        3. Format the content appropriately for the chosen content type
        4. Make the content engaging, accurate, and valuable to the audience
        5. Do not mention that this information comes from Wikipedia
        6. Focus on providing value and insights about the topic
        7. Use facts from the provided content but write in your own words
        """
        
        result = generate_content(prompt)
        return result
    
    except ContentGenerationError:
        raise
    except Exception as e:
        raise ContentGenerationError(f"Error transforming topic content: {str(e)}")
