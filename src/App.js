import React, { useState, useEffect } from 'react';
import { apiUrl } from './config';

function App() {
  const [currentWord, setCurrentWord] = useState('Loading...');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${apiUrl}/word`)
      .then(res => res.json())
      .then(data => {
        setCurrentWord(data.word);
      })
      .catch(error => {
        console.error('Error:', error);
        setError(error.message);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        {error ? (
          <p>Error: {error}</p>
        ) : (
          <p>The current word is: {currentWord}</p>
        )}
      </header>
    </div>
  );
}

export default App;