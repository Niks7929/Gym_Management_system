"""
SETFIT DARK RAGE - Application Entrypoint (app.py)
Unified entrypoint pointing directly to the modular application factory.
"""
import os
from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    print(f"🔥 SETFIT DARK RAGE Server Starting on http://127.0.0.1:{port} (Debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)
