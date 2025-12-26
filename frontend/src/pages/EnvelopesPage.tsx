import { Link } from 'react-router-dom';

export default function EnvelopesPage() {
    return (
        <div className="p-4 space-y-4">
            <h2 className="text-2xl font-bold">Your Daily Envelopes</h2>
            <p className="text-muted-foreground">You have 3 unchecked envelopes.</p>

            <div className="grid gap-4">
                {/* Mock Envelopes */}
                {[1, 2, 3].map((id) => (
                    <div key={id} className="p-4 rounded-lg border border-border bg-card shadow-sm">
                        <h3 className="font-semibold">Candidate #{id}</h3>
                        <p className="text-sm text-muted-foreground mb-2">90% Compatibility</p>
                        <Link
                            to={`/threads/${id}`}
                            className="text-sm font-medium text-primary hover:underline"
                        >
                            Open Thread
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}
