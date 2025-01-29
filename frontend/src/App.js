import './App.css';
import './PdfUploadButton/PdfUploadButton.js';
import PdfUploadButton from './PdfUploadButton/PdfUploadButton.js';
import { useQuery } from 'react-query';
import { useState } from 'react';

export default function App() {
  const [fileNames, setFileNames] = useState([]);

  function addFileName(fileName) {
    setFileNames((prevFileNames) => [...prevFileNames, fileName]);
  }

  const { status } = useQuery('session', async () => {
    await fetch('http://localhost:8000/api/session', { method: 'POST', credentials: 'include' });
  });
  
  if (status === 'loading') {
    return (
      <div className="App">
        <h1>Connecting...</h1>
      </div>
    );
  }

  return (
    <div className="App">
      <h1>web-pdf</h1>
      <PdfUploadButton addFileName={addFileName}/>
      <ol>
        {fileNames.map((fileName, index) => (
          <li key={index}>{fileName}</li>
        ))}
      </ol>
    </div>
  );
}
