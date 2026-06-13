from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI
import base64
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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



user_credits = {}

@app.post("/generate", response_class=HTMLResponse)
def generate(prompt: str = Form(...), request: Request = None):

    user_id = request.client.host

    if user_id not in user_credits:
        user_credits[user_id] = 10

    if user_credits[user_id] <= 0:
        return "<h2>❌ No credits left. Please buy more.</h2>"

    user_credits[user_id] -= 1

    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"High quality YouTube food thumbnail: {prompt}",
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json

    return f"""
    <h2>✅ Generated Thumbnail</h2>

    <p>Credits left: {user_credits[user_id]}</p>

    <img src="data:image/png;base64,{image_base64}" style="width:400px; border-radius:10px;" />

    <br><br>

    <a download="thumbnail.png" href="data:image/png;base64,{image_base64}">
        <button style="
            padding: 12px 18px;
            border: none;
            border-radius: 8px;
            background: #ff3b3b;
            color: white;
            font-weight: bold;
            cursor: pointer;
        ">
            ⬇ Download Image
        </button>
    </a>

       <br><br>

    <a href="/">⬅ Generate another</a>

    """
