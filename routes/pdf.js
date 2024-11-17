//code for pdf summarizer backend
// ./routes/pdf.js
const express = require('express');
const router = express.Router();
const multer = require('multer');
const { spawn } = require('child_process');

const upload = multer({ dest: 'uploads/' });

router.post('/summarize', upload.single('pdf'), (req, res) => {
  const pdfPath = req.file.path;

  // Spawn Python process to summarize the PDF
  const pythonProcess = spawn('python', ['ai/pdf_summarizer.py', 'summarize', pdfPath]);

  let summary = '';

  pythonProcess.stdout.on('data', (data) => {
    summary += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error summarizing PDF' });
    }
    res.json({ summary });
  });
});

router.post('/question', (req, res) => {
  const { question, context } = req.body; // Now also receiving context (summary) from the frontend

  if (!context) {
    return res.status(400).json({ error: 'Context (summary) is required for question answering' });
  }

  // Spawn Python process to answer the question using the provided context (summary)
  const pythonProcess = spawn('python', ['ai/pdf_summarizer.py', 'question', question, context]);

  let answer = '';

  pythonProcess.stdout.on('data', (data) => {
    answer += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error answering question' });
    }
    res.json({ answer });
  });
});

module.exports = router;
