import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface BlurRevealProps {
    revealLevel: number; // 0 to 100
    children: React.ReactNode;
    className?: string;
}

export function BlurReveal({ revealLevel, children, className }: BlurRevealProps) {
    // revealLevel 0 -> max blur (e.g. 20px)
    // revealLevel 100 -> no blur (0px)

    // Calculate blur amount: linear mapping for now
    // 0 -> 24px
    // 100 -> 0px
    const maxBlur = 24;
    const blurAmount = maxBlur - (revealLevel / 100) * maxBlur;

    // Calculate opacity: maybe faded at 0?
    // Let's keep opacity full but just blurred, or slightly lower opacity
    // if very blurred to simulate "hidden". 
    // For now just blur.

    return (
        <div className={cn("relative overflow-hidden", className)}>
            <motion.div
                animate={{ filter: `blur(${blurAmount}px)` }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className="w-full h-full"
            >
                {children}
            </motion.div>

            {/* Optional: Overlay if reveal is 0 to prevent selecting text? */}
            {revealLevel < 100 && (
                <div className="absolute inset-0 z-10 select-none" />
            )}
        </div>
    );
}
