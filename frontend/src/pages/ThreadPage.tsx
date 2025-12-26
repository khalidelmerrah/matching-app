import { useParams } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { BlurReveal } from '@/components/BlurReveal';
import { ThreadSocket } from '@/lib/socket';
import { Send, Lock } from 'lucide-react';

interface Message {
    id: string;
    sender: 'me' | 'them';
    content: string;
    timestamp: Date;
}

export default function ThreadPage() {
    const { id } = useParams<{ id: string }>();
    // Mock reveal level for now, fetch from API later
    const [revealLevel, setRevealLevel] = useState(10);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [connected, setConnected] = useState(false);
    const socketRef = useRef<ThreadSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!id) return;

        // Connect to socket
        const token = 'dev-token'; // In real app get from auth context/storage
        socketRef.current = new ThreadSocket(id, token, (data) => {
            console.log('Got message:', data);
            // Handle incoming message
            // setMessages(prev => [...prev, mappedMessage]);
        });
        setConnected(true);

        return () => {
            socketRef.current?.close();
        };
    }, [id]);

    const sendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        // Optimistic add
        const newMsg: Message = {
            id: Date.now().toString(),
            sender: 'me',
            content: input,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, newMsg]);
        setInput('');

        // In real app, socket.send(...) or POST /api/threads/:id/messages
        // For now dealing with visual UI
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* Mock content to show blur */}
                <div className="flex justify-center my-4">
                    <BlurReveal revealLevel={revealLevel} className="p-4 bg-muted rounded-lg max-w-xs text-center text-sm">
                        <h4 className="font-semibold mb-1">Profile Photo</h4>
                        <div className="w-24 h-24 bg-gray-300 rounded-full mx-auto mb-2" />
                        <p>Reveal level: {revealLevel}%</p>
                    </BlurReveal>
                </div>

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[70%] rounded-lg p-3 text-sm ${msg.sender === 'me'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-border bg-card">
                <form onSubmit={sendMessage} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="flex-1 px-4 py-2 rounded-full border border-input bg-background focus:outline-none focus:ring-1 focus:ring-ring"
                        placeholder="Type a message..."
                    />
                    <button
                        type="submit"
                        className="p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}
