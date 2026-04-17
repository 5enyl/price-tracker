from flask import Flask, render_template
from datetime import datetime
from search_newegg import search_newegg
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    parts = conn.execute('SELECT id, name, category, price, last_updated, brand, model, base_model FROM parts').fetchall()
    conn.close()
    return render_template('index.html', parts=parts)

@app.route('/history/<int:part_id>')
def part_history(part_id):
    conn = get_db()
    part = conn.execute('SELECT name FROM parts WHERE id = ?', (part_id,)).fetchone()
    prices = conn.execute(
        'SELECT price, timestamp FROM price_history WHERE part_id = ? ORDER BY timestamp',
        (part_id,)
    ).fetchall()
    conn.close()
    return render_template('history.html', part=part, prices=prices)

@app.route('/search')
def search():
    return render_template('search.html', results=[], query='')

@app.route('/search', methods=['POST'])
def search_post():
    from flask import request
    query = request.form.get('query', '')
    results = search_newegg(query)
    return render_template('search.html', results=results, query=query)

@app.route('/add_part', methods=['POST'])
def add_part():
    from flask import request, redirect
    conn = get_db()
    conn.execute('''
        INSERT INTO parts (name, category, price, url, last_updated, brand, model, base_model)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request.form.get('name'),
        request.form.get('category'),
        float(request.form.get('price') or 0),
        request.form.get('url'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        request.form.get('brand'),
        request.form.get('model') or None,
        request.form.get('base_model')
    ))
    conn.commit()
    conn.close()
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)

    