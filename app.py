from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import random

app = FastAPI()

def get_suggestions(keyword):
    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={keyword}"
        return requests.get(url).json()[1]
    except:
        return []

def is_buyer(kw):
    words = ["buy","price","shop","αγορά","τιμή","gift","δώρο"]
    return any(w in kw.lower() for w in words)

def score(kw):
    comp = random.randint(10, 80)
    demand = len(kw.split()) * 10
    buyer = 30 if is_buyer(kw) else 0
    return {
        "keyword": kw,
        "score": demand + buyer - comp,
        "competition": comp
    }

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>🚀 SEO Tool</h1>
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

    rows = ""
    for r in results:
        rows += f"<tr><td>{r['keyword']}</td><td>{r['score']}</td><td>{r['competition']}</td></tr>"

    return f"""
    <h2>Results for: {kw}</h2>
    <table border="1">
    <tr><th>Keyword</th><th>Score</th><th>Competition</th></tr>
    {rows}
    </table>
    <br><a href="/">Back</a>
    """
