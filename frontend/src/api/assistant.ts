import axios from 'axios'

const ASSISTANT_URL = import.meta.env.VITE_ASSISTANT_URL || 'http://localhost:8003/api/assistant/v1'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatResponse {
  reply: string
  suggested_chips: string[]
}

export const assistantApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await axios.post(`${ASSISTANT_URL}/chat/`, {
      message,
    })
    return response.data
  },
}
