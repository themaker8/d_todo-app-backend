from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins temporarily
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        address = request.args.get('address')
        print(f"Getting tasks for address: {address}")  # Debug log
        
        if not address:
            return jsonify({"error": "Address is required"}), 400
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('SELECT * FROM tasks WHERE user_address = ?', (address,))
        tasks = c.fetchall()
        conn.close()
        
        result = [{
            'id': task[0],
            'user_address': task[1],
            'title': task[2],
            'description': task[3],
            'due_date': task[4],
            'priority': task[5],
            'status': task[6],
            'created_at': task[7]
        } for task in tasks]
        
        print(f"Returning tasks: {result}")  # Debug log
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting tasks: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        print(f"Received task data: {data}")  # Debug log
        
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
        
        print(f"Created task with ID: {task_id}")  # Debug log
        return jsonify({"message": "Task created", "id": task_id})
        
    except Exception as e:
        print(f"Error creating task: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
