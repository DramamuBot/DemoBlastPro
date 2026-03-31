import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLASTPRO_DIR = os.path.join(BASE_DIR, 'blastpro')

if BLASTPRO_DIR not in sys.path:
    sys.path.insert(0, BLASTPRO_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
