import json
import mimetypes
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).parent
dist = root / 'frontend' / 'dist'
shots = root / '.visual-shots'
shots.mkdir(exist_ok=True)

category = {'id': 1, 'name': 'Программы и экскурсии', 'slug': 'programs'}


def excursion(number):
    multi = number == 2
    slot = {
        'id': number, 'date': '2027-10-14', 'time': '10:00:00',
        'end_date': '2027-10-15' if multi else '2027-10-14',
        'end_time': '15:00:00', 'max_participants': 20,
        'available_seats': 18, 'is_available': True,
        'price_override': '2500.00' if multi else None,
    }
    return {
        'id': number, 'slug': f'program-{number}',
        'title': 'Двухдневная программа по Омску' if multi else 'Пешеходная экскурсия по Омску',
        'short_description': 'Маршрут по городу с гидом.',
        'description': 'Маршрут по городу с гидом.',
        'category': category, 'location_type_display': 'Город',
        'tour_format_display': 'Пешеходная', 'group_size': 20,
        'price': '1500.00', 'duration': 2040 if multi else 300,
        'is_multi_day': multi, 'main_image': None, 'images': [],
        'nearest_slots': [slot], 'slots': [slot],
        'ticket_types': [{'id': number, 'name': 'Взрослый', 'price': '1500.00', 'is_active': True}],
        'average_rating': None, 'review_count': 0,
        'program_days': [], 'approved_reviews': [], 'rating_distribution': {},
        'is_active': True,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/api/'):
            if path in ('/api/excursions/1/', '/api/excursions/2/'):
                data = excursion(int(path.split('/')[-2]))
            elif path == '/api/excursions/':
                data = {'count': 2, 'next': None, 'previous': None,
                        'results': [excursion(1), excursion(2)]}
            elif path == '/api/excursions/categories/':
                data = [category]
            elif path == '/api/excursions/max-price/':
                data = {'max_price': 2500}
            else:
                data = {}
            payload = json.dumps(data).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
        else:
            file = (dist / path.lstrip('/')).resolve()
            if not file.is_relative_to(dist.resolve()) or not file.is_file():
                file = dist / 'index.html'
            payload = file.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(file)[0] or 'text/html')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    result = subprocess.run(['node', '.tmp_visual.cjs'], cwd=root, capture_output=True, timeout=90)
    print(result.stdout.decode(errors='replace'))
    print(result.stderr.decode(errors='replace'))
    if result.returncode:
        raise SystemExit(result.returncode)
finally:
    server.shutdown()
