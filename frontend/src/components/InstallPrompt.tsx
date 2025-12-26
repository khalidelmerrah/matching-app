import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Share } from "lucide-react"; // Using DivideSquare as placeholder for "Add to Home Screen" icon if needed, or just generic

export function InstallPrompt() {
    const [showPrompt, setShowPrompt] = useState(false);

    useEffect(() => {
        // Detect iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
        // Detect if standalone
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone;

        if (isIOS && !isStandalone) {
            // Show prompt after a small delay
            const timer = setTimeout(() => setShowPrompt(true), 2000);
            return () => clearTimeout(timer);
        }
    }, []);

    return (
        <AnimatePresence>
            {showPrompt && (
                <motion.div
                    initial={{ y: "100%" }}
                    animate={{ y: 0 }}
                    exit={{ y: "100%" }}
                    className="fixed bottom-0 left-0 right-0 z-50 p-4 pb-8 bg-background border-t border-border shadow-2xl"
                >
                    <div className="flex flex-col items-center gap-4 max-w-sm mx-auto text-center">
                        <h3 className="text-lg font-semibold">Install Slowburn</h3>
                        <p className="text-sm text-muted-foreground">
                            To use Slowburn, add it to your home screen for the full experience.
                        </p>
                        <div className="flex items-center gap-2 text-sm">
                            <span>Tap</span>
                            <Share className="w-5 h-5 text-primary" />
                            <span>then "Add to Home Screen"</span>
                        </div>
                        <button
                            onClick={() => setShowPrompt(false)}
                            className="text-xs text-muted-foreground underline mt-2"
                        >
                            Dismiss
                        </button>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
