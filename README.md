# youtube-transcript-microservice

Python Flask microservice to fetch YouTube transcripts for MichaStocksBot.
Bypasses Google Cloud IP blocking by running on Render.com infrastructure.

## Deploy to Render.com

1. Go to https://render.com and sign up / log in
2. Click **New** → **Web Service**
3. Connect your GitHub account and select this repository: `symonlevy/youtube-transcript-microservice`
4. Render will auto-detect `render.yaml` — click **Apply**
5. Wait ~2 minutes for the first deploy
6. Copy your service URL (e.g. `https://youtube-transcript-microservice.onrender.com`)

## Keep-Alive (Important for Free Tier)

Render Free tier sleeps after 15 minutes of inactivity. Add a cron job in Google Apps Script to ping `/health` every 10 minutes:

```javascript
function keepAlive() {
  var url = 'https://YOUR-APP.onrender.com/health';
  UrlFetchApp.fetch(url, { muteHttpExceptions: true });
}
// In setupTriggers(), add:
// ScriptApp.newTrigger('keepAlive').timeBased().everyMinutes(10).create();
```

## Update CONFIG in Apps Script

In your MichaStocksBot Apps Script, update the CONFIG object:

```javascript
TRANSCRIPT_API_URL: 'https://YOUR-APP.onrender.com',
```

Then update `getVideoTranscript()` function:

```javascript
function getVideoTranscript(videoId, preferredLang) {
  if (!CONFIG.TRANSCRIPT_API_URL) return null;
  try {
    var lang = preferredLang || 'en';
    var url = CONFIG.TRANSCRIPT_API_URL + '/transcript?v=' + videoId + '&lang=' + lang;
    var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var data = JSON.parse(resp.getContentText());
    if (data.ok && data.text) {
      return { text: data.text.substring(0, CONFIG.TRANSCRIPT_MAX_CHARS || 3000), language: lang };
    }
    return null;
  } catch(e) {
    logError('getVideoTranscript', e, { videoId: videoId });
    return null;
  }
}
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /transcript?v=VIDEO_ID&lang=he` | Fetch transcript for a video |
| `GET /health` | Health check |
| `GET /` | Service info |

## Files

- `app.py` — Flask application
- `requirements.txt` — Python dependencies
- `render.yaml` — Render.com deployment config
