# -*- coding: utf-8 -*-
from flask import Flask, request, render_template_string
from datetime import date, timedelta
import socket
import platform

app = Flask(__name__)

# --- Wklejona konfiguracja z Twojego pliku harmonogram.py ---
CYCLE_START = date(2026, 6, 24)
CYCLE_LEN = 28

SHIFT_PATTERN = {
    0:  ('dzienna',  '07:00-19:00'),
    1:  ('dzienna',  '07:00-19:00'),
    2:  ('dzienna',  '07:00-19:00'),
    3:  ('dzienna',  '07:00-19:00'),
    7:  ('nocna',    '19:00-07:00'),
    8:  ('nocna',    '19:00-07:00'),
    9:  ('nocna',    '19:00-07:00'),
    10: ('nocna',    '19:00-07:00'),
    14: ('dzienna',  '07:00-19:00'),
    15: ('dzienna',  '07:00-19:00'),
    16: ('dzienna',  '07:00-19:00'),
    21: ('nocna',    '19:00-07:00'),
    22: ('nocna',    '19:00-07:00'),
    23: ('nocna',    '19:00-07:00'),
}

DAY_NAMES = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela']

def parse_date(s: str) -> date:
    s = s.strip()
    # format domyślny z input-HTML typu 'date': RRRR-MM-DD
    if len(s) >= 10 and s[4] == '-':
        return date.fromisoformat(s[:10])
    s = s.replace('/', '.').replace('-', '.')
    parts = s.split('.')
    if len(parts) != 3:
        raise ValueError("Oczekiwano formatu DD.MM.RRRR")
    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
    return date(y, m, d)

def get_shift(d: date):
    if d < CYCLE_START:
        return 'przed_startem', None, None, 'Data przed startem harmonogramu'
    offset = (d - CYCLE_START).days % CYCLE_LEN
    if offset in SHIFT_PATTERN:
        typ, godz = SHIFT_PATTERN[offset]
        adnotacja = ''
        if typ == 'nocna':
            nastepny = d + timedelta(days=1)
            if d.weekday() == 5 or nastepny.weekday() == 5 or d.weekday() == 6 or nastepny.weekday() == 6:
                adnotacja = 'spierdolona przez Ryobi'
        return 'pracujący', typ, godz, adnotacja
    return 'wolne', None, None, ''

# HTML jako szablon strony w przeglądarce
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Harmonogram Zmian - Artura Kotarskiego</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; color: #333; margin: 40px auto; max-width: 600px; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: white;}
        h2 { color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        input[type="date"], input[type="submit"] { padding: 10px; font-size: 16px; margin: 10px 0; width: 100%; box-sizing: border-box; }
        input[type="submit"] { background-color: #28a745; color: white; border: none; cursor: pointer; transition: 0.3s; font-weight: bold;}
        input[type="submit"]:hover { background-color: #218838; }
        .result { margin-top: 20px; padding: 15px; border-left: 5px solid #007bff; background: #e9ecef; border-radius: 4px; }
        .alert { color: #dc3545; font-weight: bold; background-color: #f8d7da; padding: 10px; border-radius: 4px; border: 1px solid #f5c6cb; margin-top: 10px; }
        .footer { font-size: 11px; color: #6c757d; margin-top: 35px; text-align: center; border-top: 1px solid #dee2e6; padding-top: 15px; }
    </style>
</head>
<body>
    <h2>Harmonogram Zmian 12h - Cykl 4-tygodniowy</h2>
    <p><strong>Autor:</strong> Artura Kotarskiego (zawieszona w chmurze AWS)</p>
    
    <form method="POST">
        <label for="search_date">Wybierz datę do sprawdzenia:</label>
        <input type="date" id="search_date" name="search_date" required value="{{ default_date }}">
        <input type="submit" value="Sprawdź zmianę">
    </form>

    {% if error %}
        <div class="alert">Błąd: {{ error }}</div>
    {% endif %}

    {% if result %}
        <div class="result">
            <h3>Wynik wyszukiwania:</h3>
            <p><strong>Data:</strong> {{ check_date }} ({{ day_name }})</p>
            <p><strong>Status:</strong> {{ status }}</p>
            {% if shift_type %}
                <p><strong>Zmiana:</strong> <span style="text-transform: uppercase; font-weight: bold;">{{ shift_type }}</span> ({{ shift_hours }})</p>
            {% endif %}
            {% if adnotacja %}
                <p class="alert" style="margin-top: 10px;"><strong>Ostrzeżenie:</strong> {{ adnotacja }}</p>
            {% endif %}
        </div>
    {% endif %}

    <div class="footer">
        Aplikacja uruchomiona w Python {{ python_version }} na serwerze produkcyjnym: {{ hostname }}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    hostname = socket.gethostname()
    python_version = platform.python_version()
    default_date = date.today().isoformat()
    
    if request.method == 'POST':
        date_str = request.form.get('search_date')
        try:
            target_date = parse_date(date_str)
            status, typ, godz, adnotacja = get_shift(target_date)
            day_name = DAY_NAMES[target_date.weekday()]
            
            return render_template_string(
                HTML_TEMPLATE,
                default_date=date_str,
                result=True,
                check_date=target_date.strftime('%d.%m.%Y'),
                day_name=day_name,
                status=status.upper(),
                shift_type=typ,
                shift_hours=godz,
                adnotacja=adnotacja,
                python_version=python_version,
                hostname=hostname
            )
        except Exception as e:
            return render_template_string(
                HTML_TEMPLATE,
                default_date=default_date,
                error=str(e),
                python_version=python_version,
                hostname=hostname
            )
            
    return render_template_string(
        HTML_TEMPLATE,
        default_date=default_date,
        python_version=python_version,
        hostname=hostname
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
