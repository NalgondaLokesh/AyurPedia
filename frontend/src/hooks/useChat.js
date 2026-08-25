import { useChatContext } from '../context/ChatContext';

export const useChat = () => {
  return useChatContext();
};

export default useChat;
