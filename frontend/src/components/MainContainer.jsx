import React from 'react';

const MainContainer = ({ children }) => (
  <div
    style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: '#1a1a1a',
      color: '#fff',
      padding: '2vw',
      boxSizing: 'border-box',
      width: '100vw',
    }}
  >
    {children}
  </div>
);

export default MainContainer; 