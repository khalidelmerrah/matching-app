export class ThreadSocket {
    private ws: WebSocket | null = null;
    private url: string;
    private onMessage: (data: any) => void;
    private shouldReconnect = true;
    private retryDelay = 1000;

    constructor(threadId: string, token: string, onMessage: (data: any) => void) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        this.url = `${protocol}//${host}/ws/threads/${threadId}?token=${token}`;
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
