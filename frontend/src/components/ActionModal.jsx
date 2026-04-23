/**
 * Modal component for approving/denying suggested actions
 */

import { useState } from 'react';

export default function ActionModal({ action, onApprove, onDeny, onClose }) {
  const [isProcessing, setIsProcessing] = useState(false);

  if (!action) return null;

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      await onApprove(action.id, true);
      onClose();
    } catch (error) {
      console.error('Error approving action:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeny = async () => {
    setIsProcessing(true);
    try {
      await onDeny(action.id, false);
      onClose();
    } catch (error) {
      console.error('Error denying action:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            🤖 Suggested Action
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isProcessing}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Action Description */}
        <div className="mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <h4 className="font-medium text-blue-900 mb-2">
              {action.description}
            </h4>
            {action.reasoning && (
              <p className="text-blue-700 text-sm">
                <strong>Why:</strong> {action.reasoning}
              </p>
            )}
          </div>

          {/* Action Details */}
          {action.details && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-gray-700 text-sm">
                <strong>Details:</strong> {action.details}
              </p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={handleApprove}
            disabled={isProcessing}
            className="flex-1 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing...
              </div>
            ) : (
              '✅ Approve'
            )}
          </button>

          <button
            onClick={handleDeny}
            disabled={isProcessing}
            className="flex-1 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing...
              </div>
            ) : (
              '❌ Decline'
            )}
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-4 text-xs text-gray-500 text-center">
          The assistant will only perform actions you explicitly approve
        </div>
      </div>
    </div>
  );
}