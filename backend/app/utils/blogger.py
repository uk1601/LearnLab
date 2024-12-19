import os
import pickle
import markdown
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from ..core.logger import setup_logger
import json
import tempfile
load_dotenv()
logger=setup_logger(__name__)
def authenticate_blogger_api():
    SCOPES = ['https://www.googleapis.com/auth/blogger']
    creds = None
    token_path = 'token.pickle'

    # Load credentials from environment variable
    credentials_string = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_string:
        logger.error("GOOGLE_API_CREDENTIALS environment variable is missing.")
        raise ValueError("GOOGLE_API_CREDENTIALS environment variable is missing.")
    
    # Parse the JSON string and save it to a temporary file
    try:
        credentials_data = json.loads(credentials_string)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(json.dumps(credentials_data).encode())
            credentials_path = temp_file.name
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in GOOGLE_API_CREDENTIALS: {e}")
        raise



    # # Load the JSON credentials from .env file
    # credentials_path = os.getenv('GOOGLE_API_CREDENTIALS')
    # print(credentials_path)
    # if not credentials_path or not os.path.exists(credentials_path):
    #     logger.error("Invalid or missing BLOGGER_API_CREDENTIALS environment variable.")
    #     raise ValueError("Invalid or missing BLOGGER_API_CREDENTIALS environment variable.")

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, 
                SCOPES,
                redirect_uri='http://localhost:8081/'
            )
            creds = flow.run_local_server(port=8081)
            
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('blogger', 'v3', credentials=creds)

def get_blog_id(service):
    try:
        blogs = service.blogs()
        result = blogs.listByUser(userId='self').execute()
        if 'items' in result and len(result['items']) > 0:
            print(f"Found {len(result['items'])} blogs")
            return result['items'][0]['id']
        else:
            print("No blogs found for this user. Please create a blog first at blogger.com")
            return None
    except Exception as e:
        print(f"Error retrieving blog ID: {str(e)}")
        return None
    
def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
            
            # Try to get title from first header
            title = None
            for line in content:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            
            # If no header found, use first non-empty line
            if not title:
                for line in content:
                    if line.strip():
                        title = line.strip()
                        break
            
            # Convert full content to HTML
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables',
                'markdown.extensions.toc'
            ])
            html_content = md.convert(''.join(content))
            
            return title, html_content
    except Exception as e:
        print(f"Error reading markdown file: {str(e)}")
        return None, None


def create_blog_post(service, blog_id, title, html_content):
    posts = service.posts()
    body = {
        'kind': 'blogger#post',
        'title': title,
        'content': html_content
    }
    
    return posts.insert(blogId=blog_id, body=body, isDraft=False).execute()

def parse_markdown_content(content: str):
    """Parse markdown content string and return title and HTML content."""
    try:
        lines = content.splitlines()
            
        # Try to get title from first header
        title = None
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        # If no header found, use first non-empty line
        if not title:
            for line in lines:
                if line.strip():
                    title = line.strip()
                    break
        
        # Convert full content to HTML
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc'
        ])
        html_content = md.convert(content)
        
        return title, html_content
    except Exception as e:
        print(f"Error parsing markdown content: {str(e)}")
        return None, None
def convert_markdown_to_html(markdown_text):
    import markdown
    return markdown.markdown(markdown_text)

def main():
    markdown_file_path = 'post.md'
    
    try:
        # First authenticate and get service
        service = authenticate_blogger_api()
        
        # Then get blog ID
        blog_id = get_blog_id(service)
        
        if blog_id:
            # Read and convert markdown content
            title, html_content = read_markdown_file(markdown_file_path)
            if title and html_content:
                result = create_blog_post(service, blog_id, title, html_content)
                print(f"Post published successfully: {result['url']}")
            else:
                print("Could not read markdown file")
        else:
            print("Could not retrieve blog ID")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
