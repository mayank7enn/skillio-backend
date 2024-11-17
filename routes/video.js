const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');

router.post('/summarize', (req, res) => {
  const { videoUrl } = req.body;

  const pythonProcess = spawn('python', ['ai/video_summarizer.py', videoUrl]);

  let summary = '';

  pythonProcess.stdout.on('data', (data) => {
    summary += data.toString();
    console.log('Received data from Python:', summary);  // Debug log
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error summarizing video' });
    }
    res.json({ summary });
  });
});

module.exports = router;
