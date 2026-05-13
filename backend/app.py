from flask import Flask
from flask_cors import CORS


from api.record_api import record_bp
from api.list_api import list_bp
from api.dictation_content import dictation_content_bp
from api.wav_file import wav_file_bp
from api.upload_result import upload_result_bp
from api.login import login_bp
from api.record_api import record_bp
from api.custom_dictation import custom_dictation_bp
from api.register import register_bp
def create_app():
    """
    Flask 应用工厂函数
    便于后期扩展、测试和部署
    """
    app = Flask(__name__)

    # 解决微信小程序跨域问题
    CORS(app)

    # 基础配置
    app.config.from_object('config')

    # 注册蓝图
    app.register_blueprint(record_bp, url_prefix='/api/record')
    app.register_blueprint(list_bp, url_prefix='/api/list')
    app.register_blueprint(dictation_content_bp, url_prefix='/api/dictation_content')
    app.register_blueprint(wav_file_bp, url_prefix='/api/wav_file')
    app.register_blueprint(upload_result_bp, url_prefix='/api/upload_result')
    app.register_blueprint(login_bp, url_prefix='/api/login')
    app.register_blueprint(custom_dictation_bp, url_prefix='/api/custom_dictation')
    app.register_blueprint(register_bp, url_prefix='/api/register')
    # 健康检查接口（测试服务是否启动）
    @app.route('/')
    def index():
        return {
            "code": 200,
            "msg": "OCR Dictation System Backend Running"
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
