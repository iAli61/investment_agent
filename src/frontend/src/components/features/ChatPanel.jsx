import React, { useState, useRef, useEffect } from 'react';
import { formatCurrency } from '../../utils/formatters';

const ChatPanel = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m your Property Investment AI Assistant. How can I help you analyze your investment today?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // In a real implementation, this would be an API call to your backend
      // For now, we'll simulate a response after a delay
      setTimeout(() => {
        // Simulate AI response
        const assistantResponse = {
          id: messages.length + 2,
          role: 'assistant',
          content: getSimulatedResponse(inputValue),
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, assistantResponse]);
        setIsLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
    }
  };

  // Simple function to simulate AI responses
  const getSimulatedResponse = (query) => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('property') && lowerQuery.includes('analyze')) {
      return "Great! Let's analyze a property. Could you provide the address and purchase price?";
    } else if (lowerQuery.includes('address') || lowerQuery.includes('location')) {
      return "Thanks for the address. I'll gather market data for this location. What's the asking price for this property?";
    } else if (lowerQuery.includes('price') || lowerQuery.includes('euro') || lowerQuery.includes('€')) {
      const price = formatCurrency(500000);
      return `Thank you. For a property at this price (${price}), I'll need to gather some more information about the property type and condition. Is this an apartment, house, or multi-family property?`;
    } else if (lowerQuery.includes('financing') || lowerQuery.includes('mortgage')) {
      return "Let's look at financing options. What down payment percentage are you considering? The typical range is between 10% and 30%.";
    } else if (lowerQuery.includes('rent')) {
      return "Based on the location and property details you've provided, I estimate the monthly rental income would be between €1,800 and €2,200. Would you like me to provide a more detailed rent analysis?";
    } else if (lowerQuery.includes('roi') || lowerQuery.includes('return')) {
      return "Based on the information provided, this investment has an estimated ROI of 6.8% and a cash-on-cash return of 4.2%. The cap rate is approximately 5.3%. Would you like to see a detailed breakdown?";
    } else {
      return "I understand you're looking for investment insights. To help you better, could you provide more specific details about the property you're considering?";
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Messages area */}
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-3/4 p-3 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white text-gray-800 border border-gray-200'
                }`}
              >
                <p>{message.content}</p>
                <span className="text-xs opacity-70 mt-1 block">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-3/4 p-3 rounded-lg bg-white text-gray-800 border border-gray-200">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef}></div>
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type a message..."
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition-colors disabled:opacity-50"
            disabled={isLoading || !inputValue.trim()}
          >
            <span className="material-icons">send</span>
          </button>
        </form>
        <div className="mt-3 flex flex-wrap gap-2">
          <button className="text-xs bg-gray-100 text-gray-700 py-1 px-2 rounded-full hover:bg-gray-200">
            Analyze a property
          </button>
          <button className="text-xs bg-gray-100 text-gray-700 py-1 px-2 rounded-full hover:bg-gray-200">
            Calculate financing
          </button>
          <button className="text-xs bg-gray-100 text-gray-700 py-1 px-2 rounded-full hover:bg-gray-200">
            Estimate rental income
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;