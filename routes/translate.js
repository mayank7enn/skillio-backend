// ./routes/translate.js
const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');

router.post('/', (req, res) => {
  const { inputText, action } = req.body;

  if (!inputText || !action) {
    return res.status(400).json({ error: 'Input text and action are required' });
  }

  // Spawn Python process for translation and TTS
  const pythonProcess = spawn('python', [
    'ai/translator.py',
    inputText,
    action
  ]);

  let result = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    result += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
    console.error(`Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ 
        error: 'Error processing translation',
        details: error 
      });
    }

    try {
      // Parse the JSON result from Python
      const { outputText, audioPath } = JSON.parse(result.trim());
      
      res.json({
        outputText,
        audioUrl: audioPath
      });
    } catch (err) {
      console.error('Error parsing Python output:', err);
      res.status(500).json({ 
        error: 'Error processing translation results',
        details: err.message 
      });
    }
  });
});

module.exports = router;