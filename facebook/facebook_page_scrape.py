import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get URL and headers from environment variables
url = os.getenv("FACEBOOK_URL")
headers = json.loads(os.getenv("FACEBOOK_HEADERS"))

def get_facebook_posts(url, headers, max_pages=200):
    posts = []
    
    # Create a session object
    with requests.Session() as session:
        session.headers.update(headers)  # Update session headers

        for _ in range(max_pages):
            try:
                response = session.get(url)
                response.raise_for_status()  # Raise an error for bad status codes
                
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract posts and their times
                for post in soup.find_all('article'):
                    # Extract post content
                    post_content = ''.join([p.get_text() for p in post.find_all('p')])
                    
                    # Extract post time
                    time_tag = post.find('abbr')
                    post_time = time_tag.get_text() if time_tag else 'Unknown'
                    
                    print(f"Post Content: {post_content}")
                    print(f"Post Time: {post_time}")
                    posts.append([post_content, post_time])
                
                # Find the next page URL by text content
                next_link = soup.find('a', string='See more stories')
                if next_link:
                    next_page_url = next_link['href']
                    url = urljoin("https://mbasic.facebook.com", next_page_url)
                else:
                    break
            
            except Exception as e:
                # Save posts to Excel if an error occurs
                df = pd.DataFrame(posts, columns=['Post Content', 'Post Time'])
                df.to_excel('facebook_posts.xlsx', index=False, engine='openpyxl')
                print(f"An error occurred: {e}")
                print("Posts have been saved to 'facebook_posts.xlsx'")
                raise  # Re-raise the exception after saving

    return posts

try:
    posts = get_facebook_posts(url, headers)
    df = pd.DataFrame(posts, columns=['Post Content', 'Post Time'])
    df.to_excel('facebook_posts.xlsx', index=False, engine='openpyxl')
    print("Posts have been saved to 'facebook_posts.xlsx'")
except Exception as e:
    print(f"An error occurred during the scraping process: {e}")
    # Optionally save any data collected before the error
    if posts:
        df = pd.DataFrame(posts, columns=['Post Content', 'Post Time'])
        df.to_excel('facebook_posts.xlsx', index=False, engine='openpyxl')
        print("Posts have been saved to 'facebook_posts.xlsx'")
