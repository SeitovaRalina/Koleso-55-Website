import json
import re
import subprocess
from pathlib import Path

directory = Path(__file__).parent
result = subprocess.run(['gh', 'pr', 'view', '8', '--json', 'body'], check=True, capture_output=True, text=True, encoding='utf-8')
body = json.loads(result.stdout)['body']
addendum = (directory / 'pr-addendum.md').read_text(encoding='utf-8')
if '## Дополнение: русификация Django Admin' not in body:
    body = body.rstrip() + '\n' + addendum
body = body.replace('Миграция `bookings.0004` меняет только отображаемые подписи и подсказки полей.',
                    'Миграции `bookings.0004` и `bookings.0005` меняют только отображаемые подписи, подсказки и имя модели.')
for caption in ('Django Admin: список и сохраненный статус, 1440x900',
                'Django Admin: список и фильтры, 390x844'):
    body = re.sub(r'\n*!\[' + re.escape(caption) + r'\]\([^)]*\)', '', body)
(directory / 'pr-body.md').write_text(body.rstrip() + '\n', encoding='utf-8')
