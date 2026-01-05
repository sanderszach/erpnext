import React, { useState, useRef, useEffect, useMemo } from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  HStack, 
  Text, 
  Input, 
  IconButton, 
  Container, 
  Separator,
  ChakraProvider,
  defaultSystem,
  createSystem,
  defaultConfig
} from '@chakra-ui/react';
import { Send, User, Bot, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

export function ChatContent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your ERP Assistant. How can I help you today?",
      sender: 'agent',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Simulate agent response
    setTimeout(() => {
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm processing your request. This is a simulated response from the microfrontend.",
        sender: 'agent',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    }, 1000);
  };

  return (
    <Container maxW="3xl" h="100%" display="flex" flexDirection="column" p={0}>
      <Flex 
        direction="column" 
        h="full" 
        bg="white" 
        rounded="xl" 
        shadow="md" 
        border="1px solid" 
        borderColor="gray.100"
        overflow="hidden"
      >
        {/* Header */}
        <Flex px={6} py={4} align="center" justify="space-between" bg="gray.50" borderBottom="1px solid" borderColor="gray.100">
          <HStack gap={3}>
            <Box bg="blue.600" p={2} rounded="lg">
              <Sparkles size={20} color="white" />
            </Box>
            <Box>
              <Text fontWeight="bold" fontSize="md">ERP Assistant</Text>
            </Box>
          </HStack>
        </Flex>

        {/* Messages Area */}
        <VStack 
          flex={1} 
          overflowY="auto" 
          p={6} 
          gap={6} 
          align="stretch"
          css={{
            '&::-webkit-scrollbar': { width: '4px' },
            '&::-webkit-scrollbar-track': { background: 'transparent' },
            '&::-webkit-scrollbar-thumb': { background: '#e2e8f0', borderRadius: '10px' },
          }}
        >
          {messages.map((msg) => (
            <Flex key={msg.id} gap={4} direction={msg.sender === 'user' ? 'row-reverse' : 'row'}>
              <Box 
                w="32px" 
                h="32px" 
                rounded="full" 
                bg={msg.sender === 'user' ? 'blue.100' : 'gray.100'} 
                display="flex" 
                alignItems="center" 
                justifyContent="center"
                flexShrink={0}
              >
                {msg.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
              </Box>
              <Box 
                maxW="80%" 
                bg={msg.sender === 'user' ? 'blue.600' : 'gray.50'} 
                color={msg.sender === 'user' ? 'white' : 'gray.800'}
                p={3} 
                px={4}
                rounded="2xl"
                roundedTopRight={msg.sender === 'user' ? '4px' : '2xl'}
                roundedTopLeft={msg.sender === 'agent' ? '4px' : '2xl'}
                shadow="sm"
              >
                <Text fontSize="sm" lineHeight="tall">{msg.text}</Text>
                <Text fontSize="10px" mt={1} opacity={0.6} textAlign={msg.sender === 'user' ? 'right' : 'left'}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </Box>
            </Flex>
          ))}
          <div ref={messagesEndRef} />
        </VStack>

        <Separator />

        {/* Input Area */}
        <Box p={4} bg="white">
          <HStack gap={2}>
            <Input 
              placeholder="Message ERP Assistant..." 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              variant="subtle"
              size="lg"
              rounded="full"
              bg="gray.50"
              _focus={{ bg: 'white', borderColor: 'blue.500', boxShadow: 'none' }}
            />
            <IconButton
              aria-label="Send message"
              onClick={handleSend}
              rounded="full"
              colorPalette="blue"
              size="lg"
              disabled={!inputValue.trim()}
            >
              <Send size={18} />
            </IconButton>
          </HStack>
          <Text fontSize="xs" color="gray.400" textAlign="center" mt={2}>
            Agent can make mistakes. Check important info.
          </Text>
        </Box>
      </Flex>
    </Container>
  );
};

function Chat() {
  // // Create a stable system instance for the MFE context
  // // This ensures the Chakra system is properly initialized even when loaded dynamically
  // const system = useMemo(() => {
  //   // Use defaultSystem if available, otherwise create a new one
  //   if (defaultSystem) {
  //     return defaultSystem;
  //   }
  //   return createSystem(defaultConfig);
  // }, []);

  return (
    <ChakraProvider value={defaultSystem}>
      <ChatContent />
    </ChakraProvider>
  );
};

export default Chat;
