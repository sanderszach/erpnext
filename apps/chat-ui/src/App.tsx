import React from 'react';
import { ChakraProvider, defaultSystem } from '@chakra-ui/react';
import { ChatContent } from './components/Chat';

const App = () => {
  return (
    <ChakraProvider value={defaultSystem}>
      <div style={{ padding: '20px' }}>
        <ChatContent />
      </div>
    </ChakraProvider>
  );
};

export default App;
