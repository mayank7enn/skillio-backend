const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/video');
const helpdeskRoutes = require('./routes/helpdesk');
const pdfRoutes = require('./routes/pdf');
const translateRouter = require('./routes/translate');
const path = require('path'); 

const app = express();

app.use(cors());
app.use(express.json());

// mongoose.connect('mongodb://localhost/skillio', {
//   useNewUrlParser: true,
//   useUnifiedTopology: true,
// });
app.get('/', (req, res) => {
  res.send('Skillio API is running');
});

app.use('/api/video', videoRoutes);
app.use('/api/helpdesk', helpdeskRoutes);
app.use('/api/pdf', pdfRoutes);
app.use('/api/translate', translateRouter);
// In your main Express app file
app.use('/audio', express.static(path.join(__dirname, 'public/audio')));

module.exports = app;
