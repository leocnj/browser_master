const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const app = express();

app.use(cors());
app.use(express.json());

const db = new sqlite3.Database(':memory:');
db.serialize(() => {
    db.run(`CREATE TABLE employees (
        id TEXT PRIMARY KEY, 
        name TEXT, 
        ssn TEXT, 
        gender TEXT, 
        salary TEXT, 
        dental_plan TEXT, 
        vision_plan TEXT, 
        medical_plan TEXT
    )`);
    db.run(`INSERT INTO employees VALUES 
        ('123', 'John Doe', 'XXX-XX-1234', 'Male', '$85,000', 'Basic Dental', 'No Vision', 'Standard Medical'),
        ('456', 'Jane Smith', 'XXX-XX-5678', 'Female', '$120,000', 'Premium Dental', 'Premium Vision', 'Gold Medical')
    `);
});

app.get('/', (req, res) => res.send('Mock HR Backend is running!'));

app.get('/api/employee/:id', (req, res) => {
    db.get("SELECT * FROM employees WHERE id = ?", [req.params.id], (err, row) => {
        res.json(row || { error: 'Not found' });
    });
});

app.post('/api/employee/:id/benefits', (req, res) => {
    const { dental_plan, vision_plan, medical_plan } = req.body;
    db.run(
        "UPDATE employees SET dental_plan = ?, vision_plan = ?, medical_plan = ? WHERE id = ?", 
        [dental_plan, vision_plan, medical_plan, req.params.id], 
        () => {
            res.json({ success: true });
        }
    );
});

app.listen(3000, () => console.log('Mock HR backend running on port 3000'));
