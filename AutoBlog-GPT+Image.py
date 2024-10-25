# Install OpenAI before run the py file
pip install openai
pip install requests

import openai
import requests 
import random 
import re
from collections import Counter
import re
import os

openai.api_key = 'YOUR_API_KEY'

# Function to get related keywords based on provided keywords
def get_related_keywords(provided_keywords):
    prompt = f"Based on the provided keywords '{provided_keywords}', list 10 related keywords or phrases, seperate by ,."
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=150,
        temperature=0.6,
        n=1,
        stop=None,
        timeout=15,
        seed=random.randint(0, 1000000)
    )
    related_keywords = response.choices[0].text.strip().split(', ')
    return related_keywords

# Function to generate random blog ideas
def generate_blog_ideas(keywords, industry):
    prompt = f"Based on the keywords '{keywords}' and the industry '{industry}', provide 5 unique blog ideas."
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=15,
        seed=random.randint(0, 1000000)
    )
    ideas = response.choices[0].text.strip().split('\n')
    return ideas

# Generate SEO blog title, meta and content
def generate_seo_blog(topic, industry, length, tone):
    prompt = (f"As a senior SEO content writer, your task is to craft SEO articles about {topic} based on my text."
             f"I need an article that is over {length} words long. To write effective content, two important factors are perplexity and burstiness."
             f"Perplexity measures the complexity of text, while burstiness looks at the variations in sentence length and structure."
             f"Humans tend to write with more burstiness, including both longer and shorter sentences, while AI-generated sentences tend to be more uniform."
             f"For the content I am requesting, I need a good level of perplexity and burstiness, but please avoid using those exact terms. If you undertand, write a blog for me in the {industry} with a {tone} tone. My keywords are: {keywords}." 
             f"Please ensure the content has a high degree of perplexity and burstiness."
             "Start your response with tags [TITLE] (made the title compeling and contains {extended_keywords}), [META] (write meta description here), and [CONTENT]") # Optional: future references (include h1, h2, h3... tags in the final output where appropriate)

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        # max_tokens=3800,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=15,
        seed=random.randint(0, 1000000)
    )

    

    raw_blog = response.choices[0].text.strip()
    title = raw_blog.split("[TITLE]")[1].split("[META]")[0].strip()
    meta = raw_blog.split("[META]")[1].split("[CONTENT]")[0].strip()
    content = raw_blog.split("[CONTENT]")[1].strip()

    return title, meta, content

# Funtion to get alt text for image
def generate_summary(paragraph):
    """Generate a one-sentence summary for a given paragraph."""
    prompt = f"Summarize in short sentence:\n\n\"{paragraph}\""
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=80,  # Set a limit to get only a one-sentence summary
        temperature=0.7,
        n=1,
        stop=[".", "!", "?"],  # Stop at the end of a sentence.
        timeout=15,
        seed=random.randint(0, 1000000)
    )
    return response.choices[0].text.strip()

# Function to fetch image from Unsplash
def fetch_image_url_from_unsplash(alt_text):
    API_URL = "YOUR_API_URL"
    API_KEY = "YOUR_API_KEY" 

    response = requests.get(API_URL, params={
        "query": alt_text,  # use the alt text as the query
        "client_id": API_KEY,
        "per_page": 2
    })

    data = response.json()
    if data["results"]:
        # randomly choose one of the results
        chosen_image = random.choice(data["results"])
        return chosen_image["urls"]["regular"]
    return None

# List of common stop words; you might want to expand on this based on your requirements
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", 
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 
    'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', 
    "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
    "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def extract_keywords(text):
    # Lowercase the text to ensure consistency
    text = text.lower()
    
    # Remove any punctuation and split the text into words
    words = re.findall(r'\w+', text)
    
    # Remove stop words
    cleaned_words = [word for word in words if word not in STOP_WORDS]
    
    # (Optional) Count and retrieve most common words; this might be useful if you're dealing with long text
    word_counts = Counter(cleaned_words)
    most_common_words = [item[0] for item in word_counts.most_common()]
    
    return most_common_words

# Function to add images to content
def add_images_to_content(content):
    paragraphs = content.split("\n\n")
    num_paragraphs = len(paragraphs)
    
    # If the content doesn't have many paragraphs, reduce the indices to ensure images appear
    if num_paragraphs < 5:
        image_indices = [num_paragraphs // 2]
    else:
        image_indices = [num_paragraphs * 2 // 8, num_paragraphs * 6 // 8]
    
    combined_paragraphs = []
    within_list = False

    for i, para in enumerate(paragraphs):
        # Check if the paragraph is part of a list
        if re.match(r'^\d+\.', para) or ("•" in para or "-" in para or "*" in para):
            within_list = True
        elif within_list:
            within_list = False
            i -= 1  # Adjust index to insert the image after the list

        combined_paragraphs.append(para)

        if i in image_indices and not within_list:
            preceding_content = "\n\n".join(combined_paragraphs)
            alt_text = generate_summary(preceding_content)
            alt_keywords = extract_keywords(alt_text)
            image_url = fetch_image_url_from_unsplash(alt_keywords)  # Using alt_text here 
            
            combined_paragraphs.append(f'<img src="{image_url}" alt="{alt_text}">')

    return "\n\n".join(combined_paragraphs)



# Elaborate on blog content
def elongate_content(content):
    paragraphs = [para.strip() for para in content.split('\n') if para]
    elongated_paragraphs = []

    for para in paragraphs:
        prompt = f"Elaborate further on the following paragraph, providing deeper insights and more details, keep SEO format:\n\n{para}"
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=200,  # Sufficient tokens to ensure expansion of each paragraph
            temperature=0.7,
            n=1,
            stop=None,
            timeout=20,  # Extended the timeout slightly
            seed=random.randint(0, 1000000)
        )
        elongated_paragraphs.append(response.choices[0].text.strip())

    return "\n\n".join(elongated_paragraphs)

# Get user inputs
# keywords = input("Enter keywords: ") 
related_keywords = get_related_keywords(keywords)
extended_keywords = ", ".join([keywords] + related_keywords)
# print(f"Generated Keywords:\n {extended_keywords}")

# industry = input("Enter industry: ")
# tone = input("Enter tone: ")

# Automatically select a random blog idea
blog_ideas = generate_blog_ideas(extended_keywords, industry)
selected_idea = random.choice(blog_ideas)
# print(f"\nSelected Blog Idea: {selected_idea}\n")

# Generate the blog content based on the selected idea
blog_title, blog_meta, blog_content = generate_seo_blog(selected_idea, industry, 2000, tone) # Standard blog 

# Add images at the 3/8 and 6/8 positions of the blog content.
# blog_content_with_images = add_images_to_content(blog_content)


# # Elongate the blog content for a richer narrative
# elongated_blog_content = elongate_content(blog_content)

# Print the generated sections
print(f"{blog_title}\n") # Print Blog Title
print(f"Meta Description: {blog_meta}\n") # Print Meta Description
print(blog_content)  # Print the content

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

# Function to create and write to a new file
def create_blog_file(title, meta, content, folder_path="."):
    filename = sanitize_filename(title) + ".txt"  # Assuming .txt format
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\n\n")
        file.write(f"Meta Description: {meta}\n\n")
        file.write(content)

# Optionally, specify a folder path or use the current directory
folder_path = "YOUR_PATH" 

create_blog_file(blog_title, blog_meta, blog_content, folder_path)