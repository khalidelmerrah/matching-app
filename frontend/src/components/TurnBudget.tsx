import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { DivideSquare } from 'lucide-react';

interface TurnBudgetProps {
    className?: string;
    onBudgetExhausted?: (exhausted: boolean) => void;
}

export function TurnBudget({ className, onBudgetExhausted }: TurnBudgetProps) {
    const [budget, setBudget] = useState<{ remaining: number; total: number } | null>(null);

    useEffect(() => {
        // Mock fetch for now, replace with API call
        // GET /api/users/me/budget
        // For now mock response
        setBudget({ remaining: 5, total: 10 });

        // In real implementation:
        // fetch('/api/users/me/budget', { headers: { Authorization: `Bearer ${token}` } })
        //   .then(...)
    }, []);

    useEffect(() => {
        if (budget && onBudgetExhausted) {
            onBudgetExhausted(budget.remaining <= 0);
        }
    }, [budget, onBudgetExhausted]);

    if (!budget) return null;

    return (
        <div className={cn("flex items-center gap-2 p-2 rounded-lg bg-secondary", className)}>
            <div className="text-xs font-medium uppercase text-muted-foreground">Turns</div>
            <div className="flex gap-1">
                {Array.from({ length: budget.total }).map((_, i) => (
                    <div
                        key={i}
                        className={cn(
                            "w-2 h-4 rounded-sm transition-colors",
                            i < budget.remaining ? "bg-primary" : "bg-muted-foreground/30"
                        )}
                    />
                ))}
            </div>
            <div className="text-sm font-bold ml-1">{budget.remaining}</div>
        </div>
    );
}
