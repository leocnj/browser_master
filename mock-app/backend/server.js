const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const app = express();

app.use(cors());
app.use(express.json());

const db = new sqlite3.Database(':memory:');
db.serialize(() => {
    db.run("CREATE TABLE employees (id TEXT PRIMARY KEY, dental TEXT)");
    db.run("INSERT INTO employees VALUES ('123', 'Basic Plan')");
});

app.get('/api/employee/:id', (req, res) => {
    db.get("SELECT * FROM employees WHERE id = ?", [req.params.id], (err, row) => {
        res.json(row || { error: 'Not found' });
    });
});

app.post('/api/employee/:id/dental', (req, res) => {
    db.run("UPDATE employees SET dental = ? WHERE id = ?", [req.body.dental, req.params.id], () => {
        res.json({ success: true });
    });
});

app.listen(3000, () => console.log('Mock HR backend running on port 3000'));
