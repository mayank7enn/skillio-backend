const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');

router.post('/query', (req, res) => {
  const { query } = req.body;

  const pythonProcess = spawn('python', ['ai/helpdesk_ai.py', query]);

  let answer = '';

  pythonProcess.stdout.on('data', (data) => {
    answer += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error processing query' });
    }
    res.json({ answer });
  });
});

module.exports = router;