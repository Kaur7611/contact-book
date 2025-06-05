from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory contacts list
contacts = [
    {"id": 1, "name": "Alice", "phone": "1234567890"},
    {"id": 2, "name": "Bob", "phone": "0987654321"},
]

def get_contact(contact_id):
    return next((c for c in contacts if c["id"] == contact_id), None)

@app.route('/')
def index():
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        new_id = max(c["id"] for c in contacts) + 1 if contacts else 1
        name = request.form['name']
        phone = request.form['phone']
        contacts.append({"id": new_id, "name": name, "phone": phone})
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = get_contact(contact_id)
    if not contact:
        return "Contact not found", 404
    if request.method == 'POST':
        contact['name'] = request.form['name']
        contact['phone'] = request.form['phone']
        return redirect(url_for('index'))
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    global contacts
    contacts = [c for c in contacts if c["id"] != contact_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)








