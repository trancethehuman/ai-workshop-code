import os
import threading
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from pyngrok import ngrok, conf
from typing import List, Dict
import ssl
import certifi
import urllib.request
from dotenv import load_dotenv

load_dotenv()

# Fix SSL certificate verification issues globally
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = (
    ssl._create_unverified_context
)  # For development only
urllib.request.urlopen = lambda url, **kwargs: urllib.request.urlopen(
    url, context=ssl_context, **kwargs
)

# Initialize FastAPI
app = FastAPI()

# Store crawl results
crawl_completed = asyncio.Event()
crawl_results = []


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(f"\nReceived webhook event: {data}")

    if data["type"] == "crawl.completed":
        print("\nCrawling completed!")
        crawl_completed.set()

    elif data["type"] == "crawl.page":
        # Store the extracted data
        if "data" in data and len(data["data"]) > 0:
            crawl_results.extend(data["data"])
        print(f"\nReceived page data: {len(crawl_results)} pages processed")

    elif data["type"] == "crawl.failed":
        print(f"Crawl failed: {data.get('error', 'Unknown error')}")

    elif data["type"] == "crawl.started":
        print("Crawl started")


def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()


async def start_webhook_server():
    """Start the webhook server and return the webhook URL"""
    # Setup ngrok with SSL context
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    if not ngrok_token:
        raise ValueError("NGROK_AUTH_TOKEN environment variable not set")

    conf.get_default().auth_token = ngrok_token
    conf.get_default().ssl_context = ssl_context

    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Start ngrok tunnel with retries
    max_retries = 3
    for attempt in range(max_retries):
        try:
            tunnel = ngrok.connect(8000)
            webhook_url = f"{tunnel.public_url}/webhook"
            print(f"Webhook URL: {webhook_url}")
            return webhook_url
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(1)


def stop_webhook_server():
    """Stop the webhook server and clean up"""
    try:
        ngrok.disconnect()
    except:
        pass


if __name__ == "__main__":
    # Test the webhook server
    async def test():
        webhook_url = await start_webhook_server()
        print(f"Webhook server running at {webhook_url}")
        try:
            # Keep the server running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            stop_webhook_server()

    asyncio.run(test())
