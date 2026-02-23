from flask import Blueprint, request, jsonify

tts_bp = Blueprint('tts', __name__)


@tts_bp.route('/synthesize', methods=['POST'])
def synthesize():
    """
    语音合成接口
    文字 -> 语音文件 URL
    """
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({
            "code": 400,
            "msg": "Text is empty"
        })

    # TODO: 调用 TTS service
    audio_url = "/uploads/audio/demo.mp3"

    return jsonify({
        "code": 200,
        "msg": "TTS success",
        "data": {
            "audio_url": audio_url
        }
    })
