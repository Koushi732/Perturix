import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';
import { Button } from './Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center w-full h-full min-h-[400px] p-8 text-center animate-in fade-in duration-200">
          <div className="w-16 h-16 bg-rose-500/10 rounded-full flex items-center justify-center mb-6">
            <AlertTriangle className="w-8 h-8 text-rose-500" aria-hidden="true" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Something went wrong</h2>
          <p className="text-slate-300 max-w-md mb-8 text-sm">
            {this.state.error?.message || "An unexpected error occurred while rendering this component."}
          </p>
          <Button variant="primary" onClick={this.handleRetry} aria-label="Try again">
            <RefreshCcw className="w-4 h-4 mr-2" aria-hidden="true" />
            Try Again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
