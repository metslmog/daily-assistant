/**
 * Chat API service for communicating with the agent
 */

const API_BASE_URL = 'http://127.0.0.1:5001';

export class ChatAPI {
  /**
   * Send a message to the agent and get response
   * @param {string} message - User message
   * @param {string} sessionId - Optional session ID
   * @returns {Promise<Object>} - Agent response
   */
  static async sendMessage(message, sessionId = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
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
        throw new Error(`Chat API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Get chat history for the current session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Array>} - Chat history
   */
  static async getChatHistory(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/history?session_id=${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`Chat history API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  }

  /**
   * Approve or deny a suggested action
   * @param {string} actionId - Action ID
   * @param {boolean} approved - Whether to approve the action
   * @returns {Promise<Object>} - Action result
   */
  static async approveAction(actionId, approved) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/actions/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action_id: actionId,
          approved,
        }),
      });

      if (!response.ok) {
        throw new Error(`Action API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error approving action:', error);
      throw error;
    }
  }

  /**
   * Get current agent status
   * @returns {Promise<Object>} - Agent status
   */
  static async getAgentStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent/status`);
      
      if (!response.ok) {
        throw new Error(`Agent status API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching agent status:', error);
      throw error;
    }
  }
}