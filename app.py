from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    parts = conn.execute('SELECT id, name, category, price, last_updated FROM parts').fetchall()
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

if __name__ == '__main__':
    app.run(debug=True)

    