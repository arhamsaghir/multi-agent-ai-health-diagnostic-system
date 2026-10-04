"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RefreshCw
} from "lucide-react";
import { cn } from "@/lib/utils";
import { sendChatMessage } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const quickQuestions = [
  "What are the symptoms of pneumonia?",
  "How is diabetes diagnosed?",
  "What causes chest pain?",
  "Symptoms of heart disease",
  "When to see a doctor for fever?",
];

export function MedicalChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your medical Q&A assistant. You can ask me questions about health conditions, symptoms, treatments, and more. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Connect to live FastAPI backend (/api/chat/message)
      const chatRes = await sendChatMessage(messageText, conversationId);
      if (chatRes.conversationId) {
        setConversationId(chatRes.conversationId);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: chatRes.reply,
        timestamp: chatRes.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.warn("Backend chat unavailable, using local guidance:", err);

      const responses: Record<string, string> = {
        "pneumonia": "Pneumonia is an infection that inflames the air sacs in one or both lungs. Common symptoms include: productive cough, fever with chills, shortness of breath, chest pain, and fatigue.",
        "diabetes": "Diabetes is a chronic condition affecting glucose regulation. Symptoms include frequent urination, increased thirst, unexplained weight loss, and fatigue.",
        "chest pain": "Chest pain should always be evaluated promptly. If accompanied by radiating pain, shortness of breath, or sweating, contact emergency services (112 / 108) immediately.",
        "heart disease": "Common symptoms include chest discomfort, shortness of breath, palpitations, and fatigue with exertion.",
        "fever": "A fever is generally a body temperature above 100.4°F (38°C). Seek immediate care if accompanied by stiff neck, confusion, or difficulty breathing.",
      };

      let fallbackResponse = "I understand you have questions about medical symptoms. While I can provide general health information, please consult a healthcare provider for clinical evaluation.";
      const lowerInput = messageText.toLowerCase();
      for (const [key, value] of Object.entries(responses)) {
        if (lowerInput.includes(key)) {
          fallbackResponse = value;
          break;
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: fallbackResponse,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 text-white">
          <Bot size={20} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-neutral-900 dark:text-white">
            Medical Q&A Assistant
          </h1>
          <p className="text-sm text-neutral-500">
            AI-powered health information
          </p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex gap-3",
                message.role === "user" ? "flex-row-reverse" : ""
              )}
            >
              <div className={cn(
                "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                message.role === "user" 
                  ? "bg-primary-100 dark:bg-primary-900" 
                  : "bg-neutral-100 dark:bg-neutral-800"
              )}>
                {message.role === "user" ? (
                  <User size={16} className="text-primary-600" />
                ) : (
                  <Bot size={16} className="text-neutral-600 dark:text-neutral-400" />
                )}
              </div>
              <div className={cn(
                "max-w-[80%] rounded-2xl p-4",
                message.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white"
              )}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.role === "assistant" && (
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700">
                    <button
                      onClick={() => copyMessage(message.content)}
                      className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
                      title="Copy"
                    >
                      <Copy size={14} />
                    </button>
                    <button
                      className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
                      title="Helpful"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
                      title="Not helpful"
                    >
                      <ThumbsDown size={14} />
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
                <Bot size={16} className="text-neutral-600 dark:text-neutral-400" />
              </div>
              <div className="bg-neutral-100 dark:bg-neutral-800 rounded-2xl p-4">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length <= 1 && (
          <div className="px-4 pb-2">
            <p className="text-xs text-neutral-500 mb-2">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="px-3 py-1.5 text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a medical question..."
              className="flex-1 px-4 py-3 rounded-xl bg-neutral-100 dark:bg-neutral-800 border-0 text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={cn(
                "px-4 py-3 rounded-xl transition-colors",
                input.trim() && !isLoading
                  ? "bg-primary-600 hover:bg-primary-700 text-white"
                  : "bg-neutral-200 dark:bg-neutral-800 text-neutral-400 cursor-not-allowed"
              )}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="text-xs text-neutral-500 mt-2 text-center">
        This is for informational purposes only. Always consult healthcare professionals for medical advice.
      </p>
    </motion.div>
  );
}