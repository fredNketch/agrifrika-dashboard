import React, { useEffect, useRef, useState } from 'react';

interface AutoScrollContainerProps {
  children: React.ReactNode;
  scrollSpeed?: number; // pixels per second
  pauseOnHover?: boolean;
  className?: string;
}

const AutoScrollContainer: React.FC<AutoScrollContainerProps> = ({ 
  children, 
  scrollSpeed = 20, 
  pauseOnHover = true,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    const content = contentRef.current;
    
    if (!container || !content) return;

    let scrollPosition = 0;
    const maxScroll = content.scrollHeight - container.clientHeight;
    
    const scroll = () => {
      if (isPaused || maxScroll <= 0) {
        animationRef.current = requestAnimationFrame(scroll);
        return;
      }

      scrollPosition += scrollSpeed / 60; // 60 FPS
      
      if (scrollPosition >= maxScroll) {
        scrollPosition = 0; // Reset to top
      }
      
      container.scrollTop = scrollPosition;
      animationRef.current = requestAnimationFrame(scroll);
    };

    if (maxScroll > 0) {
      animationRef.current = requestAnimationFrame(scroll);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [scrollSpeed, isPaused]);

  const handleMouseEnter = () => {
    if (pauseOnHover) {
      setIsPaused(true);
    }
  };

  const handleMouseLeave = () => {
    if (pauseOnHover) {
      setIsPaused(false);
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`overflow-hidden auto-scroll-container ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      <div ref={contentRef} className="w-full">
        {children}
      </div>
      <style dangerouslySetInnerHTML={{
        __html: `
          .auto-scroll-container::-webkit-scrollbar {
            display: none;
          }
        `
      }} />
    </div>
  );
};

export default AutoScrollContainer;