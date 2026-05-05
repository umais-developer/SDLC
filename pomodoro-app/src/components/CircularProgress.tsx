import React from 'react';

interface CircularProgressProps {
  progress: number; // 0–1
  sessionColor: string;
  size?: number;
  strokeWidth?: number;
  children?: React.ReactNode;
}

export function CircularProgress({
  progress,
  sessionColor,
  size = 260,
  strokeWidth = 10,
  children,
}: CircularProgressProps) {
  const center = size / 2;
  const radius = center - strokeWidth * 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.max(0, Math.min(1, progress)));
  const gradientId = `timer-grad-${sessionColor.replace('#', '')}`;

  return (
    <div
      className="circular-progress"
      style={{ width: size, height: size, position: 'relative' }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-hidden="true"
        style={{ transform: 'rotate(-90deg)', position: 'absolute', top: 0, left: 0 }}
      >
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={sessionColor} stopOpacity="1" />
            <stop offset="100%" stopColor={sessionColor} stopOpacity="0.4" />
          </linearGradient>
        </defs>
        {/* Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
        />
        {/* Progress */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {children}
      </div>
    </div>
  );
}
