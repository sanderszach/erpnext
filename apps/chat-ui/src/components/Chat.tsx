import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
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
  defaultConfig,
  Spinner
} from '@chakra-ui/react';
import { Send, User, Bot, Sparkles } from 'lucide-react';

// Agent API configuration
const AGENT_API_URL = 'http://localhost:8001';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  isLoading?: boolean;
  toolCalls?: { tool: string; args: Record<string, unknown>; result_preview: string }[];
}

interface ChatApiResponse {
  session_id: string;
  message: string;
  response: string;
  tool_calls: { tool: string; args: Record<string, unknown>; result_preview: string }[];
  error: boolean;
}

export function ChatContent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your ERP Assistant. I can help you query and manage your ERPNext data. What would you like to do?",
      sender: 'agent',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessageToAgent = useCallback(async (message: string): Promise<ChatApiResponse> => {
    const response = await fetch(`${AGENT_API_URL}/agent/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  }, [sessionId]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '',
      sender: 'agent',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const result = await sendMessageToAgent(inputValue);
      
      // Store session ID for conversation continuity
      if (result.session_id) {
        setSessionId(result.session_id);
      }

      const agentMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: result.response,
        sender: 'agent',
        timestamp: new Date(),
        toolCalls: result.tool_calls,
      };

      // Replace loading message with actual response
      setMessages((prev) => prev.slice(0, -1).concat(agentMessage));
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        sender: 'agent',
        timestamp: new Date(),
      };

      // Replace loading message with error
      setMessages((prev) => prev.slice(0, -1).concat(errorMessage));
    } finally {
      setIsLoading(false);
    }
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
                {msg.isLoading ? (
                  <HStack gap={2}>
                    <Spinner size="sm" color="blue.500" />
                    <Text fontSize="sm" color="gray.500">Thinking...</Text>
                  </HStack>
                ) : (
                  <>
                    <Text fontSize="sm" lineHeight="tall" whiteSpace="pre-wrap">{msg.text}</Text>
                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <Box mt={2} pt={2} borderTop="1px solid" borderColor="gray.200">
                        <Text fontSize="xs" color="gray.500" mb={1}>Tools used:</Text>
                        {msg.toolCalls.map((tc, idx) => (
                          <Text key={idx} fontSize="xs" color="gray.400">
                            • {tc.tool}
                          </Text>
                        ))}
                      </Box>
                    )}
                    <Text fontSize="10px" mt={1} opacity={0.6} textAlign={msg.sender === 'user' ? 'right' : 'left'}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Text>
                  </>
                )}
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
