/**
 * Main chat interface component
 */

import { useState, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import ActionModal from './ActionModal';

export default function ChatPanel({ isOpen, onClose }) {
  const [inputMessage, setInputMessage] = useState('');
  const [selectedAction, setSelectedAction] = useState(null);
  const inputRef = useRef(null);
  
  const {
    messages,
    isLoading,
    error,
    agentStatus,
    pendingActions,
    sendMessage,
    approveAction,
    clearError,
    messagesEndRef,
  } = useChat();

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    await sendMessage(inputMessage);
    setInputMessage('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content
      .split('\n')
      .map((line, index) => (
        <div key={index} className={line.trim() === '' ? 'h-2' : ''}>
          {line}
        </div>
      ));
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'user':
        return '👤';
      case 'agent':
        return '🤖';
      case 'system':
        return '⚙️';
      case 'error':
        return '❌';
      default:
        return '💬';
    }
  };

  const getMessageStyles = (type) => {
    switch (type) {
      case 'user':
        return 'bg-blue-100 border-blue-200 ml-8';
      case 'agent':
        return 'bg-gray-100 border-gray-200 mr-8';
      case 'system':
        return 'bg-green-50 border-green-200 mx-4';
      case 'error':
        return 'bg-red-50 border-red-200 mx-4';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Chat Panel */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-40 flex flex-col border-l border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-800 text-white">
          <div className="flex items-center space-x-2">
            <div className="text-xl">🤖</div>
            <div>
              <h3 className="font-semibold">Daily Assistant</h3>
              <div className="text-xs opacity-75 flex items-center space-x-1">
                <div 
                  className={`w-2 h-2 rounded-full ${
                    agentStatus === 'thinking' ? 'bg-yellow-300 animate-pulse' :
                    agentStatus === 'error' ? 'bg-red-300' : 'bg-green-300'
                  }`}
                />
                <span>
                  {agentStatus === 'thinking' ? 'Thinking...' :
                   agentStatus === 'error' ? 'Error' : 'Ready'}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 p-1"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 p-3 flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-red-700 text-sm">{error}</span>
            </div>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Pending Actions Banner */}
        {pendingActions.length > 0 && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-3">
            <div className="text-yellow-800 text-sm font-medium">
              {pendingActions.length} action(s) awaiting approval
            </div>
            <div className="mt-1">
              {pendingActions.slice(0, 2).map((action) => (
                <button
                  key={action.id}
                  onClick={() => setSelectedAction(action)}
                  className="text-yellow-700 hover:text-yellow-900 text-xs underline mr-3"
                >
                  {action.description}
                </button>
              ))}
              {pendingActions.length > 2 && (
                <span className="text-yellow-700 text-xs">
                  +{pendingActions.length - 2} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`border rounded-lg p-3 ${getMessageStyles(message.type)}`}
            >
              <div className="flex items-start space-x-2">
                <div className="text-lg">{getMessageIcon(message.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-900">
                    {formatMessage(message.content)}
                  </div>
                  
                  {/* Action Buttons */}
                  {message.actions && message.actions.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {message.actions.map((action) => (
                        <button
                          key={action.id}
                          onClick={() => setSelectedAction(action)}
                          className="block w-full text-left bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded p-2 text-sm text-blue-800 transition-colors"
                        >
                          <div className="font-medium">{action.description}</div>
                          {action.reasoning && (
                            <div className="text-xs text-blue-600 mt-1">
                              {action.reasoning}
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  )}

                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading Indicator */}
          {isLoading && (
            <div className="bg-gray-100 border border-gray-200 rounded-lg p-3 mr-8">
              <div className="flex items-center space-x-2">
                <div className="text-lg">🤖</div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your weather, commute, outfit, or anything else..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              rows="2"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          
          <div className="mt-2 text-xs text-gray-500 text-center">
            Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </div>

      {/* Action Modal */}
      <ActionModal
        action={selectedAction}
        onApprove={approveAction}
        onDeny={approveAction}
        onClose={() => setSelectedAction(null)}
      />
    </>
  );
}