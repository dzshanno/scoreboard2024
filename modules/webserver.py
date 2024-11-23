# File: modules/webserver.py

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import threading
from modules.logger import logger, LogType

def create_app(scoreboard):
    app = Flask(__name__)
    
    @app.before_request
    def record_activity():
        """Record client contact on any API request"""
        scoreboard.record_client_contact()

    @app.route('/')
    def home():
        """Serve main control interface"""
        return render_template('index.html')

    @app.route('/diagnostics')
    def diagnostics():
        """Serve diagnostics page"""
        return render_template('diagnostics.html')

    @app.route('/logs')
    def logs():
        """Serve logs viewing page"""
        return render_template('logs.html')

    # Score Management
    @app.route('/api/score', methods=['POST'])
    def update_score():
        try:
            data = request.get_json()
            team = data.get('team')
            value = data.get('score')
            user = request.headers.get('X-User-Id')
            
            if team not in ['home', 'away']:
                return jsonify({'status': 'error', 'message': 'Invalid team'}), 400
                
            scoreboard.set_score(team, value, user)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "score_update_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Timer Control
    @app.route('/api/timer', methods=['POST'])
    def update_timer():
        try:
            data = request.get_json()
            minutes = data.get('minutes', 0)
            scoreboard.set_game_time(minutes)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "timer_update_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/timer/resume', methods=['POST'])
    def resume_timer():
        try:
            scoreboard.resume_timer()
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "timer_resume_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Display Control
    @app.route('/api/display/mode', methods=['POST'])
    def set_display_mode():
        try:
            data = request.get_json()
            mode = data.get('mode')
            scoreboard.set_display_mode(mode)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "display_mode_change_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/display/power', methods=['POST'])
    def set_display_power():
        try:
            data = request.get_json()
            state = data.get('enabled', True)
            scoreboard.set_display_power(state)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "display_power_change_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/display/brightness', methods=['POST'])
    def set_brightness():
        try:
            data = request.get_json()
            level = data.get('level', 100)
            scoreboard.set_brightness(level)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "brightness_change_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/display/text', methods=['POST'])
    def set_text():
        try:
            data = request.get_json()
            text = data.get('text', '')
            scoreboard.scroll_text = text
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "text_update_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Color Control
    @app.route('/api/colors', methods=['POST'])
    def set_colors():
        try:
            data = request.get_json()
            for element, color in data.items():
                scoreboard.set_color(element, color)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.log(LogType.ERROR, "color_update_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # System Status
    @app.route('/api/status', methods=['GET'])
    def get_status():
        try:
            return jsonify({
                'scores': scoreboard.scores,
                'game_time': scoreboard.game_time,
                'display_mode': scoreboard.display_mode,
                'display_enabled': scoreboard.display_enabled,
                'brightness': scoreboard.brightness,
                'colors': scoreboard.colors,
                'timer_paused': scoreboard.timer_paused,
                'two_min_warning': scoreboard.two_min_warning,
                'power': power_manager.get_status(),
                'system': system_info.get_status()
            })
        except Exception as e:
            logger.log(LogType.ERROR, "status_fetch_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # System Updates
    @app.route('/api/update/system', methods=['POST'])
    def update_system():
        try:
            success, message = update_manager.perform_system_update()
            return jsonify({
                'success': success,
                'message': message
            })
        except Exception as e:
            logger.log(LogType.ERROR, "system_update_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/update/status', methods=['GET'])
    def get_update_status():
        try:
            return jsonify(update_manager.get_status())
        except Exception as e:
            logger.log(LogType.ERROR, "update_status_fetch_failed", {"error": str(e)})
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Error Handler
    @app.errorhandler(Exception)
    def handle_error(error):
        logger.log(LogType.ERROR, "server_error", {
            "error": str(error),
            "endpoint": request.endpoint
        })
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

    return app

# Health check endpoint for monitoring
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# Middleware for request logging
@app.after_request
def log_request(response):
    if not request.path.startswith('/health'):  # Don't log health checks
        logger.log(
            LogType.NETWORK,
            "http_request",
            {
                "method": request.method,
                "path": request.path,
                "status": response.status_code
            }
        )
    return response
