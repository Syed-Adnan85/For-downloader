from flask import Flask, request, jsonify
import yt_dlp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Function to fetch video from any website
def fetch_video(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check for <video> tags in HTML
    video_tags = soup.find_all("video")
    for video in video_tags:
        source = video.find("source")
        if source and source["src"]:
            return source["src"]

    return None

# Function to fetch dynamically loaded videos using Selenium
def fetch_dynamic_video(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    video_elements = driver.find_elements_by_tag_name("video")
    video_urls = [video.get_attribute("src") for video in video_elements if video.get_attribute("src")]

    driver.quit()
    return video_urls[0] if video_urls else None

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    
    # YouTube Video Extraction
    if "youtube.com" in url or "youtu.be" in url:
        with yt_dlp.YoutubeDL({'format': 'best'}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"video_url": info["url"]})

    # Instagram Video Extraction
    elif "instagram.com" in url:
        api_url = f"https://saveig.app/api/fetch?url={url}"
        response = requests.get(api_url).json()
        return jsonify({"video_url": response["media"][0]["url"]})

    # Other Websites - Try Standard Method
    video_url = fetch_video(url)
    if video_url:
        return jsonify({"video_url": video_url})

    # Other Websites - Try Dynamic Loading Method
    video_url = fetch_dynamic_video(url)
    if video_url:
        return jsonify({"video_url": video_url})

    return jsonify({"error": "Video not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
