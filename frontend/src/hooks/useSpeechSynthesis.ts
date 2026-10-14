import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseSpeechSynthesisReturn {
  isSupported: boolean;
  isSpeaking: boolean;
  isPaused: boolean;
  isMuted: boolean;
  speak: (text: string) => void;
  pause: () => void;
  resume: () => void;
  cancel: () => void;
  toggleMute: () => void;
  voices: SpeechSynthesisVoice[];
  selectedVoice: SpeechSynthesisVoice | null;
  setSelectedVoice: (voice: SpeechSynthesisVoice | null) => void;
}

export function useSpeechSynthesis(): UseSpeechSynthesisReturn {
  const [isSupported, setIsSupported] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);

  const synthRef = useRef<SpeechSynthesis | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);
      synthRef.current = window.speechSynthesis;

      const updateVoices = () => {
        const available = window.speechSynthesis.getVoices();
        setVoices(available);
        if (available.length > 0 && !selectedVoice) {
          // Prefer English natural voices
          const preferred =
            available.find((v) => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Samantha'))) ||
            available.find((v) => v.lang.startsWith('en')) ||
            available[0];
          setSelectedVoice(preferred);
        }
      };

      updateVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = updateVoices;
      }
    } else {
      setIsSupported(false);
    }

    return () => {
      if (synthRef.current) {
        try {
          synthRef.current.cancel();
        } catch {}
      }
    };
  }, []);

  const speak = useCallback(
    (text: string) => {
      if (!synthRef.current || isMuted || !text) return;

      try {
        synthRef.current.cancel(); // Stop prior audio
        const utterance = new SpeechSynthesisUtterance(text);
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
          setIsSpeaking(true);
          setIsPaused(false);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
          setIsPaused(false);
        };

        utterance.onerror = () => {
          setIsSpeaking(false);
          setIsPaused(false);
        };

        synthRef.current.speak(utterance);
      } catch (err) {
        console.error('Speech synthesis error:', err);
      }
    },
    [isMuted, selectedVoice]
  );

  const pause = useCallback(() => {
    if (synthRef.current && isSpeaking) {
      synthRef.current.pause();
      setIsPaused(true);
    }
  }, [isSpeaking]);

  const resume = useCallback(() => {
    if (synthRef.current && isPaused) {
      synthRef.current.resume();
      setIsPaused(false);
    }
  }, [isPaused]);

  const cancel = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
      setIsPaused(false);
    }
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => {
      const next = !prev;
      if (next && synthRef.current) {
        synthRef.current.cancel();
        setIsSpeaking(false);
      }
      return next;
    });
  }, []);

  return {
    isSupported,
    isSpeaking,
    isPaused,
    isMuted,
    speak,
    pause,
    resume,
    cancel,
    toggleMute,
    voices,
    selectedVoice,
    setSelectedVoice,
  };
}
