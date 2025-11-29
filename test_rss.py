import feedparser
import urllib.parse

# Test Google News RSS
query = "Python programming"
url = f'https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en&gl=US&ceid=US:en'

print(f"Testing URL: {url}")
print("=" * 60)

feed = feedparser.parse(url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

print(f"Status: {getattr(feed, 'status', 'N/A')}")
print(f"Total entries: {len(feed.entries)}")
print()

if hasattr(feed, 'bozo_exception'):
    print(f"Warning: {feed.bozo_exception}")
    print()

if feed.entries:
    print("First 3 articles:")
    for i, entry in enumerate(feed.entries[:3], 1):
        print(f"\n{i}. {entry.get('title', 'No title')}")
        print(f"   Link: {entry.get('link', 'No link')}")
        print(f"   Published: {entry.get('published', 'No date')}")
        summary = entry.get('summary', 'No summary')
        print(f"   Summary: {summary[:100]}...")
else:
    print("No entries found!")
    print(f"Feed keys: {feed.keys()}")
