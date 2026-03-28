from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# 🔍 Google Suggestions
def get_suggestions(keyword):
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={keyword}"
    try:
        return requests.get(url).json()[1]
    except:
        return []

# 🔍 Google Competition REAL
def get_google_results(keyword):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.google.com/search?q={keyword}"
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        stats = soup.find("div", id="result-stats")
        if stats:
            text = stats.text
            num = ''.join(filter(str.isdigit, text))
            return int(num[:6]) if num else 100000
    except:
        pass
    return 100000

# 🛒 Etsy Keywords
def get_etsy_keywords(keyword):
    url = f"https://www.etsy.com/api/v3/ajax/bespoke/member/neu/specs/marketplacesearch/autosuggest?q={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        
        suggestions = data.get("results", [])
        return [s["query"] for s in suggestions[:10]]
    
    except:
        return []

# 🧠 Buyer intent
def is_buyer(kw):
    words = ["buy","price","shop","αγορά","τιμή","gift","δώρο"]
    return any(w in kw.lower() for w in words)

# 📊 Score
def score(kw):
    comp = get_google_results(kw)
    comp_score = min(comp / 10000, 100)

    demand = len(kw.split()) * 10
    buyer = 30 if is_buyer(kw) else 0

    final = demand + buyer - comp_score

    return {
        "keyword": kw,
        "score": int(final),
        "competition": int(comp_score)
    }

# 🤖 Blog generator
def generate_blog(keyword):
    return f"""
<h3>Why {keyword} Are Trending</h3>
<p>{keyword} are one of the most unique handmade decor products.</p>
<p>Perfect as a gift and modern home decoration.</p>
"""

# 📸 Instagram ideas
def instagram(keyword):
    return [
        f"Behind the scenes making {keyword}",
        f"Close-up resin effect",
        f"Before/After transformation",
        f"Packaging your product",
        f"Customer reaction video"
    ]

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>🚀 SEO PRO TOOL</h1>
    <form action="/analyze">
        <input name="kw" placeholder="χειροποιητα ρολογια / handmade clock">
        <button>Analyze</button>
    </form>
    """

@app.get("/analyze", response_class=HTMLResponse)
def analyze(kw: str):
    suggestions = get_suggestions(kw)

    results = [score(k) for k in suggestions]
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    etsy = get_etsy_keywords(kw)
    blog = generate_blog(kw)
    insta = instagram(kw)

    rows = ""
    for r in results:
        rows += f"<tr><td>{r['keyword']}</td><td>{r['score']}</td><td>{r['competition']}</td></tr>"

    return f"""
    <h2>Results: {kw}</h2>

    <table border="1">
    <tr><th>Keyword</th><th>Score</th><th>Competition</th></tr>
    {rows}
    </table>

    <h3>🛒 Etsy Keywords</h3>
    <ul>{''.join(f"<li>{k}</li>" for k in etsy)}</ul>

    <h3>🤖 Blog Content</h3>
    {blog}

    <h3>📸 Instagram Ideas</h3>
    <ul>{''.join(f"<li>{i}</li>" for i in insta)}</ul>

    <br><a href="/">Back</a>
    """
