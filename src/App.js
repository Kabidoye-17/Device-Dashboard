import React, { useState, useEffect } from 'react';

function App() {
  const [currentWord, setCurrentWord] = useState('Loading...');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('https://kabidoye17.pythonanywhere.com/word')
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