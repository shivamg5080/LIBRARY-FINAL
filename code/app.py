from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'library.db'

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        available BOOLEAN NOT NULL DEFAULT 1
    )''')
    conn.commit()
    conn.close()

def seed_data():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM books')
    row_count = c.fetchone()[0]
    if row_count == 0:
        c.execute('''INSERT INTO books (title, author)
            VALUES
                ('Book 1', 'Author 1'),
                ('Book 2', 'Author 2'),
                ('Book 3', 'Author 3')
        ''')
        conn.commit()
    conn.close()

class Library:
    def get_books(self):
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM books')
        books = c.fetchall()
        conn.close()
        return books

    def borrow_book(self, book_id):
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE books SET available = 0 WHERE book_id =?', (book_id,))
        conn.commit()
        conn.close()

    def return_book(self, book_id):
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE books SET available = 1 WHERE book_id =?', (book_id,))
        conn.commit()
        conn.close()

    def add_book(self, title, author):
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO books (title, author) VALUES (?,?)', (title, author))
            conn.commit()
        except sqlite3.IntegrityError:
            return False
        conn.close()
        return True

library = Library()

def init_app():
    create_tables()
    seed_data()

init_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    books = library.get_books()
    return render_template('books.html', books=books)

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    book_id = int(request.form['book_id'])
    library.borrow_book(book_id)
    return redirect(url_for('books'))

@app.route('/return_book', methods=['POST'])
def return_book():
    book_id = int(request.form['book_id'])
    library.return_book(book_id)
    return redirect(url_for('books'))

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    if library.add_book(title, author):
        return redirect(url_for('books'))
    else:
        return render_template('error.html', message='Book already exists')

if __name__ == '__main__':
    app.run(debug=True)