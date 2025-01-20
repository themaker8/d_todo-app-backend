from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://d-todo-app-git-main-themaker8.vercel.app"
        ]
    }
})

# Root route for testing
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend is running!",
        "endpoints": {
            "test": "/api/test",
            "tasks": "/api/tasks",
        }
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "Backend is working!"})

# Database setup
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        user_address TEXT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400
    
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE user_address = ?', (address,))
    tasks = c.fetchall()
    conn.close()
    
    return jsonify([{
        'id': task[0],
        'user_address': task[1],
        'title': task[2],
        'description': task[3],
        'due_date': task[4],
        'priority': task[5],
        'status': task[6],
        'created_at': task[7]
    } for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    if not data or not data.get('title') or not data.get('address'):
        return jsonify({"error": "Title and address are required"}), 400
    
    task_id = str(uuid.uuid4())
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO tasks (id, user_address, title, description, due_date, priority)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        task_id,
        data['address'],
        data['title'],
        data.get('description', ''),
        data.get('due_date'),
        data.get('priority', 'medium')
    ))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task created", "id": task_id})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)