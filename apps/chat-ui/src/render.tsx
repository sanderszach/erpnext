import React from 'react';
import ReactDOM from 'react-dom/client';
import Chat from './components/Chat';

export function renderChat(container: HTMLElement) {
  const root = ReactDOM.createRoot(container);
  root.render(React.createElement(Chat));
  return root;
}

export default renderChat;

