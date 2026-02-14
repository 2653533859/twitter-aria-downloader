from flask import Flask, request, jsonify, render_template_string
import os
import requests
import json
import yt_dlp
import time
import re

app = Flask(__name__)

# Aria2 configuration
ARIA2_RPC_URL = os.getenv("ARIA2_RPC_URL", "http://localhost:6800/jsonrpc")
ARIA2_TOKEN = os.getenv("ARIA2_TOKEN", "nas123456")

# Proxy configuration
PROXY = os.getenv("PROXY", "")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Twitter to Aria2</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 600px; margin-top: 100px; }
        .card { border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .btn-twitter { background-color: #1da1f2; color: white; }
        .btn-twitter:hover { background-color: #1a91da; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card p-4">
            <h3 class="text-center mb-4">Twitter 视频推送至 Aria2</h3>
            <div class="mb-3">
                <input type="text" id="twitterUrl" class="form-control" placeholder="请输入 Twitter/X 链接">
            </div>
            <button onclick="pushToAria2()" class="btn btn-twitter w-100" id="submitBtn">解析并推送</button>
            <div id="status" class="mt-3 text-center"></div>
        </div>
    </div>

    <script>
        async function pushToAria2() {
            const url = document.getElementById('twitterUrl').value;
            const btn = document.getElementById('submitBtn');
            const status = document.getElementById('status');

            if (!url) {
                alert('请输入链接');
                return;
            }

            btn.disabled = true;
            status.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> 正在通过多源解析...';

            try {
                const response = await fetch('/api/push', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await response.json();
                if (data.success) {
                    status.innerHTML = '<span class="text-success">✅ 已成功推送到 Aria2</span>';
                    document.getElementById('twitterUrl').value = '';
                } else {
                    status.innerHTML = '<span class="text-danger">❌ 失败: ' + data.error + '</span>';
                }
            } catch (e) {
                status.innerHTML = '<span class="text-danger">❌ 错误: ' + e.message + '</span>';
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

def get_tweet_id(url):
    match = re.search(r'status/(\d+)', url)
    return match.group(1) if match else None

def get_video_url_fxtwitter(tweet_id):
    api_url = f"https://api.fxtwitter.com/i/status/{tweet_id}"
    try:
        r = requests.get(api_url, proxies={"http": PROXY, "https": PROXY}, timeout=10)
        data = r.json()
        if 'tweet' in data and 'media' in data['tweet'] and 'videos' in data['tweet']['media']:
            videos = data['tweet']['media']['videos']
            # Pick the best quality
            best_video = max(videos, key=lambda x: x.get('bitrate', 0))
            return best_video['url'], data['tweet'].get('text', 'twitter_video')[:50]
    except Exception as e:
        print(f"FxTwitter API failed: {e}")
    return None, None

def get_video_url_ytdl(twitter_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'proxy': PROXY
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(twitter_url, download=False)
            return info['url'], info.get('title', 'twitter_video')
    except Exception as e:
        print(f"yt-dlp failed: {e}")
        raise e

def push_to_aria2(video_url, title):
    filename = f"{title}_{int(time.time())}.mp4".replace("/", "_").replace(" ", "_")
    payload = {
        "jsonrpc": "2.0",
        "id": "gemini",
        "method": "aria2.addUri",
        "params": [
            f"token:{ARIA2_TOKEN}",
            [video_url],
            {
                "out": filename
            }
        ]
    }
    r = requests.post(ARIA2_RPC_URL, data=json.dumps(payload))
    return r.json()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/push', methods=['POST'])
def api_push():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL missing"})
    
    tweet_id = get_tweet_id(url)
    video_url = None
    title = "twitter_video"

    # Strategy 1: FxTwitter API (Very stable for simple videos)
    if tweet_id:
        video_url, title = get_video_url_fxtwitter(tweet_id)
    
    # Strategy 2: yt-dlp fallback
    if not video_url:
        try:
            video_url, title = get_video_url_ytdl(url)
        except Exception as e:
            return jsonify({"success": False, "error": f"解析失败: {str(e)}"})

    if video_url:
        try:
            res = push_to_aria2(video_url, title)
            if 'error' in res:
                return jsonify({"success": False, "error": res['error']['message']})
            return jsonify({"success": True, "gid": res['result']})
        except Exception as e:
            return jsonify({"success": False, "error": f"推送失败: {str(e)}"})
    
    return jsonify({"success": False, "error": "未能找到视频资源"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
