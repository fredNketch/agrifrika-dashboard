import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FacebookVideoPlayer from '../FacebookVideoPlayer';

// Mock du SDK Facebook
const mockFB = {
  Event: {
    subscribe: jest.fn(),
    unsubscribe: jest.fn(),
  },
  XFBML: {
    parse: jest.fn(),
  },
};

// Mock de window.FB
Object.defineProperty(window, 'FB', {
  value: mockFB,
  writable: true,
});

// Mock de document.createElement pour le script
const mockScript = {
  src: '',
  async: false,
  defer: false,
  onload: jest.fn(),
  onerror: jest.fn(),
};

document.createElement = jest.fn((tagName) => {
  if (tagName === 'script') {
    return mockScript as any;
  }
  return document.createElement(tagName);
});

describe('FacebookVideoPlayer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset window.FB
    delete (window as any).FB;
  });

  it('should render loading state initially', () => {
    render(<FacebookVideoPlayer videoUrl="test-url" />);
    
    expect(screen.getByText('Chargement du lecteur...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument(); // spinner
  });

  it('should load Facebook SDK when mounted', async () => {
    render(<FacebookVideoPlayer videoUrl="test-url" />);
    
    await waitFor(() => {
      expect(document.createElement).toHaveBeenCalledWith('script');
    });
  });

  it('should transform Facebook URLs correctly', async () => {
    // Mock FB as loaded
    (window as any).FB = mockFB;
    
    render(<FacebookVideoPlayer videoUrl="10153231379946729" />);
    
    await waitFor(() => {
      const fbVideoElement = document.querySelector('.fb-video');
      expect(fbVideoElement).toHaveAttribute('data-href', 'https://www.facebook.com/video.php?v=10153231379946729');
    });
  });

  it('should keep valid Facebook URLs unchanged', async () => {
    (window as any).FB = mockFB;
    
    const validUrl = 'https://www.facebook.com/facebook/videos/10153231379946729/';
    render(<FacebookVideoPlayer videoUrl={validUrl} />);
    
    await waitFor(() => {
      const fbVideoElement = document.querySelector('.fb-video');
      expect(fbVideoElement).toHaveAttribute('data-href', validUrl);
    });
  });

  it('should handle fb.watch URLs', async () => {
    (window as any).FB = mockFB;
    
    render(<FacebookVideoPlayer videoUrl="fb.watch/abc123" />);
    
    await waitFor(() => {
      const fbVideoElement = document.querySelector('.fb-video');
      expect(fbVideoElement).toHaveAttribute('data-href', 'https://fb.watch/abc123');
    });
  });

  it('should render error state for invalid URL', async () => {
    render(<FacebookVideoPlayer videoUrl="" />);
    
    await waitFor(() => {
      expect(screen.getByText('Impossible de charger la vidéo Facebook')).toBeInTheDocument();
    });
  });

  it('should call onLoad callback when video loads', async () => {
    (window as any).FB = mockFB;
    const onLoadMock = jest.fn();
    
    render(<FacebookVideoPlayer videoUrl="test-url" onLoad={onLoadMock} />);
    
    await waitFor(() => {
      expect(onLoadMock).toHaveBeenCalled();
    });
  });

  it('should call onError callback when SDK fails to load', async () => {
    const onErrorMock = jest.fn();
    
    // Mock script error
    mockScript.onerror();
    
    render(<FacebookVideoPlayer videoUrl="test-url" onError={onErrorMock} />);
    
    await waitFor(() => {
      expect(onErrorMock).toHaveBeenCalledWith('Impossible de charger le SDK Facebook');
    });
  });

  it('should apply custom width and height', async () => {
    (window as any).FB = mockFB;
    
    render(<FacebookVideoPlayer videoUrl="test-url" width={600} height={400} />);
    
    await waitFor(() => {
      const container = document.querySelector('.facebook-video-player');
      expect(container).toHaveStyle({ width: '600px', height: '400px' });
    });
  });

  it('should apply custom className', async () => {
    (window as any).FB = mockFB;
    
    render(<FacebookVideoPlayer videoUrl="test-url" className="custom-class" />);
    
    await waitFor(() => {
      const container = document.querySelector('.facebook-video-player');
      expect(container).toHaveClass('custom-class');
    });
  });

  it('should configure autoplay and loop settings', async () => {
    (window as any).FB = mockFB;
    
    render(
      <FacebookVideoPlayer 
        videoUrl="test-url" 
        autoplay={true}
        loop={true}
        allowFullscreen={true}
        showText={false}
        showCaptions={false}
      />
    );
    
    await waitFor(() => {
      const fbVideoElement = document.querySelector('.fb-video');
      expect(fbVideoElement).toHaveAttribute('data-autoplay', 'true');
      expect(fbVideoElement).toHaveAttribute('data-allowfullscreen', 'true');
      expect(fbVideoElement).toHaveAttribute('data-show-text', 'false');
      expect(fbVideoElement).toHaveAttribute('data-show-captions', 'false');
    });
  });
});

// Tests pour la fonction de transformation d'URL
describe('URL Transformation', () => {
  it('should transform video ID to full URL', () => {
    // Cette fonction est interne au composant, on teste via le rendu
    (window as any).FB = mockFB;
    
    render(<FacebookVideoPlayer videoUrl="10153231379946729" />);
    
    return waitFor(() => {
      const fbVideoElement = document.querySelector('.fb-video');
      expect(fbVideoElement).toHaveAttribute('data-href', 'https://www.facebook.com/video.php?v=10153231379946729');
    });
  });

  it('should handle empty URL', () => {
    render(<FacebookVideoPlayer videoUrl="" />);
    
    return waitFor(() => {
      expect(screen.getByText('Impossible de charger la vidéo Facebook')).toBeInTheDocument();
    });
  });
});






