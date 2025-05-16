import React from 'react';

const InputBox = () => {
  // Responsive styles
  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    background: '#232323',
    borderRadius: '1.5rem',
    padding: '0.5rem 1rem',
    width: '100%',
    maxWidth: '450px',
    margin: '0 auto 2rem auto',
    flexWrap: 'wrap',
    boxSizing: 'border-box',
    gap: '0.5rem',
  };

  const inputStyle = {
    flex: 1,
    minWidth: 0,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#fff',
    fontSize: '1rem',
    padding: '0.5rem',
  };

  // On small screens, stack buttons below input
  const isMobile = window.innerWidth <= 600;
  const buttonContainerStyle = isMobile
    ? { display: 'flex', width: '100%', justifyContent: 'space-between', marginTop: '0.5rem' }
    : { display: 'flex', alignItems: 'center' };

  return (
    <div style={containerStyle}>
      <input type="text" placeholder="Ask anything" style={inputStyle} />
      <div style={buttonContainerStyle}>
        <button style={btnStyle}>Attach</button>
        <button style={btnStyle}>Search</button>
        <button style={btnStyle}>Reason</button>
        <button style={{ ...btnStyle, background: '#444', color: '#fff', borderRadius: '50%' }}>🎤</button>
      </div>
    </div>
  );
};

const btnStyle = {
  background: 'none',
  border: 'none',
  color: '#bbb',
  marginLeft: '0.5rem',
  cursor: 'pointer',
  fontSize: '1rem',
  padding: '0.3rem 0.7rem',
};

export default InputBox; 