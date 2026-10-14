import { useState, useEffect, useRef, useCallback } from 'react';

// Browser speech recognition declarations
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export interface UseSpeechRecognitionReturn {
  isSupported: boolean;
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  setManualTranscript: (text: string) => void;
}

export function useSpeechRecognition(): UseSpeechRecognitionReturn {
  const [isSupported, setIsSupported] = useState<boolean>(false);
  const [isListening, setIsListening] = useState<boolean>(false);
  const [transcript, setTranscript] = useState<string>('');
  const [interimTranscript, setInterimTranscript] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognitionAPI) {
      setIsSupported(true);
      const recognizer = new SpeechRecognitionAPI();
      recognizer.continuous = true;
      recognizer.interimResults = true;
      recognizer.lang = 'en-US';

      recognizer.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognizer.onresult = (event: any) => {
        let finalStr = '';
        let interimStr = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i];
          if (item.isFinal) {
            finalStr += item[0].transcript + ' ';
          } else {
            interimStr += item[0].transcript;
          }
        }

        if (finalStr) {
          setTranscript((prev) => (prev ? `${prev.trim()} ${finalStr.trim()}` : finalStr.trim()));
        }
        setInterimTranscript(interimStr);
      };

      recognizer.onerror = (event: any) => {
        if (event.error === 'not-allowed') {
          setError('Microphone permission was denied. Please allow microphone access in your browser or type your answer.');
        } else if (event.error === 'no-speech') {
          // ignore or prompt candidate
        } else {
          setError(`Speech recognition notice: ${event.error}. You can edit or type your answer below.`);
        }
        setIsListening(false);
      };

      recognizer.onend = () => {
        setIsListening(false);
        setInterimTranscript('');
      };

      recognitionRef.current = recognizer;
    } else {
      setIsSupported(false);
      setError('Web Speech Recognition is not supported in this browser. Please use Chrome, Edge, or use the text fallback.');
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
      }
    };
  }, []);

  const startListening = useCallback(() => {
    setError(null);
    if (!recognitionRef.current) {
      setError('Speech recognition not available.');
      return;
    }
    try {
      recognitionRef.current.start();
    } catch (e: any) {
      // In case it was already active
      try {
        recognitionRef.current.stop();
        setTimeout(() => recognitionRef.current.start(), 200);
      } catch (err) {
        setError('Could not start microphone session.');
      }
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  const setManualTranscript = useCallback((text: string) => {
    setTranscript(text);
  }, []);

  return {
    isSupported,
    isListening,
    transcript,
    interimTranscript,
    error,
    startListening,
    stopListening,
    resetTranscript,
    setManualTranscript,
  };
}
