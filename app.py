from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.errors import TranscriptsDisabled, NoTranscriptFound
import os

app = Flask(__name__)

# Language priority order
DEFAULT_LANGS = ['he', 'iw', 'en', 'en-US', 'en-GB']


@app.route('/transcript')
def get_transcript():
    vid = request.args.get('v', '').strip()
    lang = request.args.get('lang', 'en').strip()

    if not vid:
        return jsonify({'ok': False, 'error': 'missing v parameter'}), 400

    # Build language priority: requested lang first, then defaults
    langs = [lang] + [l for l in DEFAULT_LANGS if l != lang]

    try:
        data = YouTubeTranscriptApi.get_transcript(vid, languages=langs)
        text = ' '.join([s['text'] for s in data])
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return jsonify({
            'ok': True,
            'text': text,
            'chars': len(text),
            'video_id': vid
        })
    except TranscriptsDisabled:
        return jsonify({'ok': False, 'error': 'transcripts disabled for this video'}), 404
    except NoTranscriptFound:
        return jsonify({'ok': False, 'error': 'no transcript found in requested languages'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({'ok': True, 'status': 'running'})


@app.route('/')
def index():
    return jsonify({
        'service': 'YouTube Transcript Microservice',
        'version': '1.0',
        'endpoints': {
            '/transcript?v=VIDEO_ID&lang=he': 'Get transcript for a video',
            '/health': 'Health check'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
