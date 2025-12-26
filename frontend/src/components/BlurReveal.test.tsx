import { render, screen } from '@testing-library/react';
import { BlurReveal } from './BlurReveal';
import { describe, it, expect } from 'vitest';

describe('BlurReveal', () => {
    it('renders children', () => {
        render(
            <BlurReveal revealLevel={50}>
                <div data-testid="content">Hidden Content</div>
            </BlurReveal>
        );
        expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    // Since we use framer-motion, implementation details of style might be on the motion div
    // We can check if the style attribute is present or just basic rendering for now.
});
