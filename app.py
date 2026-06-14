from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI
import base64
import os
from fastapi.responses import RedirectResponse
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("WARNING: OPENAI_API_KEY not found")
    client = None
else:
    client = OpenAI(api_key=api_key)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>AI Thumbnail Generator</title>

        <style>
            body {
                font-family: Arial;
                background: #111;
                color: white;
                text-align: center;
                padding-top: 80px;
            }

            .box {
                background: #1e1e1e;
                padding: 25px;
                border-radius: 12px;
                width: 400px;
                margin: auto;
            }

            input {
                width: 90%;
                padding: 12px;
                border-radius: 8px;
                border: none;
                margin-top: 10px;
            }

            button {
                margin-top: 15px;
                padding: 12px 18px;
                border: none;
                border-radius: 8px;
                background: red;
                color: white;
                font-weight: bold;
                cursor: pointer;
            }

            button:hover {
                background: darkred;
            }

            /* Spinner overlay */
            #loading {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }

            .dots {
                display: flex;
                gap: 6px;
            }

            .dot {
                width: 12px;
                height: 12px;
                background: white;
                border-radius: 50%;
                animation: bounce 0.6s infinite alternate;
            }

            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }

            @keyframes bounce {
                from { transform: translateY(0); opacity: 0.5; }
                to { transform: translateY(-15px); opacity: 1; }
            }
        </style>
    </head>

    <body>

        <h1>🍜 AI Thumbnail Generator</h1>

        <div class="box">
            <form method="post" action="/generate" onsubmit="showLoading()">
                <input type="text" name="prompt" placeholder="e.g. cheesy pizza explosion" required>
                <br>
                <button type="submit">Generate</button>
            </form>
        </div>

        <!-- Loading Screen -->
        <div id="loading">
            <h2>Generating your thumbnail...</h2>
            <div class="dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>

        <script>
            function showLoading() {
                document.getElementById("loading").style.display = "flex";
            }
        </script>

    </body>
    </html>
    """
from database import conn, cursor


@app.post("/generate", response_class=HTMLResponse)
def generate(prompt: str = Form(...), request: Request = None):

    if client is None:
        return "<h2>❌ OpenAI API key is not configured.</h2>"

    if request is None:
        return "<h2>Error: request missing</h2>"

    user_id = request.client.host

    cursor.execute("SELECT credits FROM credits WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute(
            "INSERT INTO credits (user_id, credits) VALUES (?, ?)",
            (user_id, 1)
        )
        conn.commit()
        user_credits = 1
    else:
        user_credits = result[0]

    print("CREDITS:", user_credits)

    if user_credits <= 0:
        return RedirectResponse(url="/no-credits", status_code=303)

    cursor.execute(
        "UPDATE credits SET credits = credits - 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()

    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"""
You are a professional YouTube thumbnail designer.

CATEGORY: Food / Mukbang / Viral food content

USER IDEA: {prompt}
""",
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json

    return f"""
<h2>✅ Generated Thumbnail</h2>

<p>Credits left: {user_credits}</p>

<img src="data:image/png;base64,{image_base64}" style="width:400px;" />

<br><br>

<a href="/">⬅ Generate another</a>
"""
@app.get("/no-credits", response_class=HTMLResponse)
def no_credits():
    return """
    <html>
    <body style="font-family: Arial; text-align:center; background:#111; color:white; padding-top:100px;">
        <h1>❌ No credits left</h1>
        <p>You used your free thumbnail.</p>

        <a href="https://thumbnail-generator.myshopify.com/products/10-thumbnail-credits">
            <button style="
                padding: 12px 18px;
                border: none;
                border-radius: 8px;
                background: green;
                color: white;
                font-weight: bold;
                cursor: pointer;
            ">
                💳 Buy More Credits
            </button>
        </a>

        <br><br>
        <a href="/">⬅ Go back</a>
    </body>
    </html>
    """