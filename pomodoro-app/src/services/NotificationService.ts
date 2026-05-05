let audioCtx: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  try {
    if (!audioCtx) {
      audioCtx = new AudioContext();
    }
    return audioCtx;
  } catch {
    return null;
  }
}

function playTone(frequency: number, duration: number, gain = 0.25): void {
  const ctx = getAudioContext();
  if (!ctx) return;
  try {
    if (ctx.state === 'suspended') {
      void ctx.resume();
    }
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';
    gainNode.gain.setValueAtTime(gain, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + duration);
  } catch {
    // Audio playback failed silently
  }
}

export const NotificationService = {
  /** Must be called inside a user-gesture handler to unlock AudioContext on iOS/Safari */
  resumeAudioContext(): void {
    const ctx = getAudioContext();
    if (ctx && ctx.state === 'suspended') {
      void ctx.resume();
    }
  },

  /** Three descending tones — work session ended */
  playWorkEndTone(): void {
    playTone(880, 0.3);
    setTimeout(() => playTone(660, 0.3), 360);
    setTimeout(() => playTone(440, 0.5), 720);
  },

  /** Three ascending tones — break ended */
  playBreakEndTone(): void {
    playTone(440, 0.3);
    setTimeout(() => playTone(660, 0.3), 360);
    setTimeout(() => playTone(880, 0.5), 720);
  },

  async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) return 'denied';
    if (Notification.permission !== 'default') return Notification.permission;
    try {
      return await Notification.requestPermission();
    } catch {
      return 'denied';
    }
  },

  notify(title: string, body: string): void {
    if (!('Notification' in window)) return;
    if (Notification.permission !== 'granted') return;
    try {
      new Notification(title, { body });
    } catch {
      // Notification failed silently
    }
  },

  getPermission(): NotificationPermission {
    if (!('Notification' in window)) return 'denied';
    return Notification.permission;
  },
};
