/**
 * Error boundary component to catch and handle errors
 */

import React, { ReactNode, ErrorInfo } from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-red-50 flex items-center justify-center p-4">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
            <div className="text-red-600 mb-4">
              <svg
                className="w-12 h-12 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4v2m0 0a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>

            <h2 className="text-lg font-bold text-gray-800 mb-2 text-center">
              Oops! Something went wrong
            </h2>

            <p className="text-gray-600 text-sm mb-4 text-center">
              We encountered an unexpected error. Please try again.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-gray-100 p-3 rounded mb-4 text-xs font-mono text-red-700 overflow-auto max-h-32">
                {this.state.error.message}
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={this.handleReset}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 font-medium"
              >
                Try Again
              </button>

              <button
                onClick={() => window.location.reload()}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 font-medium"
              >
                Reload
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              If the problem persists, try refreshing the page.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
