type Subscriber = (data: any) => void;

class SocketClient {
    private ws: WebSocket | null = null;
    private subscribers: Map<string, Set<Subscriber>> = new Map();
    private reconnectTimeout: NodeJS.Timeout | null = null;
    private token: string | null = null;

    connect(token: string) {
        if (this.ws?.readyState === WebSocket.OPEN) return;
        this.token = token;

        // In dev, we proxy /ws -> ws://localhost:8000
        // In migrated app, we might use full URL.
        // For now use relative /ws/threads/global? (Backend expects /ws/threads/{thread_id})
        // Actually backend expects connection per thread? Or global?
        // User Objective: "WebSocket client + reconnect backoff"
        // Backend: "Implemented WebSocket thread room endpoint (/ws/threads/{thread_id})"
        // So we need to manage multiple connections or one connection multiplexed?
        // Typically one connection per thread if that's how backend is built.
        // But frontend usually wants one connection for all?
        // Let's assume for now we connect to a thread when we enter it.
        // But this class looks like a singleton.
        // Let's make it a manager of connections or just generic.
        // Given the requirement "WebSocket client + reconnect backoff", I'll make a class that manages a connection to a specific URL.
    }

    // Refactoring to be a Connection Manager for specific threads?
    // Or maybe backend allows a global "user" socket?
    // Checked PROJECT_STATE: "/ws/threads/{thread_id}".
    // So client connects to specific thread.

    // Implemented as a factory or hook?
    // Let's do a simple class that connects to a URL and handles backoff.
}

export class ThreadSocket {
    private ws: WebSocket | null = null;
    private url: string;
    private token: string;
    private onMessage: (data: any) => void;
    private shouldReconnect = true;
    private retryDelay = 1000;

    constructor(threadId: string, token: string, onMessage: (data: any) => void) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        this.url = `${protocol}//${host}/ws/threads/${threadId}?token=${token}`;
        this.token = token;
        this.onMessage = onMessage;
        this.connect();
    }

    private connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('Connected to thread');
            this.retryDelay = 1000;
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.onMessage(data);
            } catch (e) {
                console.error('Failed to parse WS message', e);
            }
        };

        this.ws.onclose = () => {
            if (this.shouldReconnect) {
                console.log(`Disconnected. Retrying in ${this.retryDelay}ms...`);
                setTimeout(() => {
                    this.retryDelay = Math.min(this.retryDelay * 2, 30000);
                    this.connect();
                }, this.retryDelay);
            }
        };
    }

    public close() {
        this.shouldReconnect = false;
        this.ws?.close();
    }
}
