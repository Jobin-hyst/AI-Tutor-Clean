import React from 'react';

const actions = [
  'Summarize text',
  'Analyze data',
  'Surprise me',
  'Brainstorm',
  'More',
];

const ActionButtons = () => {
  // Responsive: wrap buttons on small screens
  const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    gap: '1rem',
    marginTop: '1.5rem',
    flexWrap: 'wrap',
    width: '100%',
    maxWidth: '600px',
  };
  const buttonStyle = {
    background: '#232323',
    color: '#ffa500',
    border: 'none',
    borderRadius: '1rem',
    padding: '0.5rem 1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    minWidth: '120px',
    marginBottom: '0.5rem',
  };
  return (
    <div style={containerStyle}>
      {actions.map((action, idx) => (
        <button
          key={action}
          style={{
            ...buttonStyle,
            opacity: idx === 0 ? 1 : 0.7,
          }}
        >
          {action}
        </button>
      ))}
    </div>
  );
};

export default ActionButtons; 