import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { HiChatBubbleLeftRight, HiPlus, HiTrash, HiClock, HiChevronLeft, HiChevronRight } from 'react-icons/hi2';
import { useAuth } from '../../context/AuthContext';

const API_BASE = 'http://localhost:8000/api';

export const ConversationSidebar = ({ isOpen, onClose, onSelectConversation, currentConversationId }) => {
  const { token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen && token) {
      fetchConversations();
    }
  }, [isOpen, token]);

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'New Conversation',
          jurisdiction: 'India',
          language: 'en'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        onSelectConversation(data.conversation_id);
        navigate('/chat');
        fetchConversations();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;

    try {
      const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setConversations(conversations.filter(c => c.conversation_id !== conversationId));
        if (currentConversationId === conversationId) {
          navigate('/chat');
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-80 bg-white dark:bg-stone-800 border-r border-stone-200 dark:border-stone-700 z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:z-0`}
      >
        {/* Header */}
        <div className="p-4 border-b border-stone-200 dark:border-stone-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100 uppercase tracking-wider">
              Conversations
            </h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 text-stone-500 hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200"
            >
              <HiChevronLeft className="w-5 h-5" />
            </button>
          </div>
          <button
            onClick={handleNewConversation}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 btn-premium text-white text-xs font-bold rounded-xl transition-all duration-300"
          >
            <HiPlus className="w-4 h-4 text-accent-300" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8">
              <HiChatBubbleLeftRight className="w-12 h-12 text-stone-300 dark:text-stone-600 mx-auto mb-3" />
              <p className="text-sm text-stone-500 dark:text-stone-400">
                No conversations yet
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.conversation_id}
                  onClick={() => {
                    onSelectConversation(conversation.conversation_id);
                    navigate('/chat');
                    if (window.innerWidth < 1024) onClose();
                  }}
                  className={`group p-3 rounded-xl cursor-pointer transition-all duration-200 ${
                    currentConversationId === conversation.conversation_id
                      ? 'bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-700'
                      : 'hover:bg-stone-50 dark:hover:bg-stone-700/50 border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-xs font-semibold text-stone-900 dark:text-stone-100 truncate mb-1">
                        {conversation.title}
                      </h3>
                      <div className="flex items-center gap-1.5 text-[10px] text-stone-500 dark:text-stone-400">
                        <HiClock className="w-3 h-3" />
                        <span>{formatDate(conversation.updated_at)}</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conversation.conversation_id, e)}
                      className="p-1.5 text-stone-400 hover:text-rose-600 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Delete conversation"
                    >
                      <HiTrash className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="mt-2 text-[10px] text-stone-400 dark:text-stone-500">
                    {conversation.message_count} message{conversation.message_count !== 1 ? 's' : ''}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-stone-200 dark:border-stone-700">
          <div className="text-[10px] text-stone-400 dark:text-stone-500 text-center">
            Conversations are saved to your account
          </div>
        </div>
      </div>
    </>
  );
};

export default ConversationSidebar;
