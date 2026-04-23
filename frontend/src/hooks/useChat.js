/**
 * React hook for managing chat state and interactions
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { ChatAPI } from '../services/chatAPI';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [agentStatus, setAgentStatus] = useState('idle');
  const [pendingActions, setPendingActions] = useState([]);
  
  const messagesEndRef = useRef(null);

  // Generate session ID on mount
  useEffect(() => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // Load chat history when session ID is available
  useEffect(() => {
    if (sessionId) {
      loadChatHistory();
    }
  }, [sessionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const history = await ChatAPI.getChatHistory(sessionId);
      setMessages(history.messages || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      // Don't set error state for history loading failures
    }
  };

  const sendMessage = useCallback(async (message) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    setAgentStatus('thinking');

    try {
      const response = await ChatAPI.sendMessage(message, sessionId);
      
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: response.message,
        timestamp: new Date().toISOString(),
        actions: response.suggested_actions || [],
      };

      setMessages(prev => [...prev, agentMessage]);
      
      // Handle suggested actions
      if (response.suggested_actions && response.suggested_actions.length > 0) {
        setPendingActions(prev => [...prev, ...response.suggested_actions]);
      }

      setAgentStatus('idle');
    } catch (error) {
      console.error('Failed to send message:', error);
      setError('Failed to send message. Please try again.');
      setAgentStatus('error');
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, isLoading]);

  const approveAction = useCallback(async (actionId, approved) => {
    try {
      const result = await ChatAPI.approveAction(actionId, approved);
      
      // Remove action from pending list
      setPendingActions(prev => prev.filter(action => action.id !== actionId));
      
      // Add confirmation message
      const confirmationMessage = {
        id: Date.now(),
        type: 'system',
        content: approved 
          ? `✅ Action approved: ${result.message}` 
          : `❌ Action declined`,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
      
      return result;
    } catch (error) {
      console.error('Failed to approve action:', error);
      setError('Failed to process action. Please try again.');
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setPendingActions([]);
    setError(null);
  }, []);

  // Add welcome message when chat starts
  useEffect(() => {
    if (messages.length === 0 && sessionId) {
      const welcomeMessage = {
        id: 'welcome',
        type: 'agent',
        content: 'Hi! I\'m your daily assistant. I can help you with information about your weather, commute, outfit suggestions, and more. What would you like to know?',
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    }
  }, [sessionId]);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    agentStatus,
    pendingActions,
    sendMessage,
    approveAction,
    clearError,
    clearChat,
    messagesEndRef,
  };
}