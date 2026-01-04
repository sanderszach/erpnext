import React from 'react';

const Chat = () => {
  return (
    <div style={{
      padding: '20px',
      border: '1px solid #ccc',
      borderRadius: '8px',
      maxWidth: '400px',
      margin: '20px auto',
      fontFamily: 'sans-serif'
    }}>
      <h2>Chat</h2>
      <div style={{
        height: '200px',
        overflowY: 'auto',
        border: '1px solid #eee',
        padding: '10px',
        marginBottom: '10px'
      }}>
        <p><strong>System:</strong> Welcome to the chat!</p>
        <p><em>This is a microfrontend component.</em></p>
      </div>
      <div style={{ display: 'flex' }}>
        <input 
          type="text" 
          placeholder="Type a message..." 
          style={{ flex: 1, padding: '8px' }}
        />
        <button style={{ padding: '8px 16px', marginLeft: '8px' }}>Send</button>
      </div>
    </div>
  );
};

export default Chat;

