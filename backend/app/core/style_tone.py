from newspaper import Article

import openai



async def extract_text_from_url(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:4000]  # Limit for token budget
    except Exception as e:
        return f"Could not extract content from {url}: {str(e)}"

async def summarize_style(text: str) -> str:
    prompt = (
"Analyze the following writing sample for \
    tone, structure, and stylistic elements. "
        "Summarize the voice characteristics in under 100 words:\n\n" + text
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response['choices'][0]['message']['content'].strip()
