import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

EXCLUDED_PATHS = ["login", "signup", "register", "signin"]  # URLs to avoid

async def fetch_page_content(browser, url):
    """Fetch page content using Playwright (JavaScript rendering)."""
    try:
        page = await browser.new_page()
        await page.goto(url, timeout=10000)  # Wait for JavaScript content
        await asyncio.sleep(2)  # Allow JS to load
        content = await page.content()
        await page.close()
        return content
    except Exception as e:
        print(f"Skipping {url} due to error: {e}")
        return None

async def scrape_website(start_url, max_pages=5):
    """Crawl and extract text from multiple pages asynchronously."""
    visited_urls = set()
    pages_to_crawl = [start_url]
    extracted_texts = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        while pages_to_crawl and len(visited_urls) < max_pages:
            url = pages_to_crawl.pop(0)
            if url in visited_urls or any(excl in url for excl in EXCLUDED_PATHS):
                continue  # Skip already visited or excluded paths
            
            print(f"Scraping: {url}")
            html = await fetch_page_content(browser, url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "html.parser")

            # Extract meaningful text
            elements = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"])
            text = "\n".join(element.get_text(strip=True) for element in elements)
            extracted_texts.append(text)

            visited_urls.add(url)

            # Extract and queue new links
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                parsed_url = urlparse(absolute_url)

                # Only add internal links and avoid re-visiting
                if parsed_url.netloc == urlparse(start_url).netloc and absolute_url not in visited_urls:
                    pages_to_crawl.append(absolute_url)

        await browser.close()

    return "\n".join(extracted_texts) if extracted_texts else "No relevant content found."

# # Example usage
# if __name__ == "__main__":
#     url = "https://example.com"  # Replace with your target website
#     scraped_content = asyncio.run(scrape_website(url, max_pages=10))
#     print(scraped_content)
