import { useCallback } from 'react';
import { NotificationService } from '../services/NotificationService';
import { StorageService } from '../services/StorageService';

interface NotificationBannerProps {
  onDismiss: (granted: boolean) => void;
}

export function NotificationBanner({ onDismiss }: NotificationBannerProps) {
  const handleAllow = useCallback(async () => {
    const permission = await NotificationService.requestPermission();
    StorageService.markNotificationBannerShown();
    onDismiss(permission === 'granted');
  }, [onDismiss]);

  const handleLater = useCallback(() => {
    StorageService.markNotificationBannerShown();
    onDismiss(false);
  }, [onDismiss]);

  return (
    <div className="notif-banner" role="status" aria-live="polite">
      <span className="notif-banner-icon" aria-hidden="true">🔔</span>
      <span className="notif-banner-text">
        Get alerts when your session ends. Enable notifications?
      </span>
      <div className="notif-banner-actions">
        <button className="btn btn--small btn--primary-ghost" onClick={handleAllow} autoFocus>
          Allow
        </button>
        <button className="btn btn--small btn--ghost" onClick={handleLater}>
          Maybe later
        </button>
      </div>
    </div>
  );
}
