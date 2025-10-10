/**
 * Unit tests for Doctor Status Indicator Component
 * Tests React component functionality, WebSocket integration, and feature flag behavior.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import WS from 'jest-websocket-mock';
import DoctorStatusIndicator, { DoctorStatus } from '../../../../../src/beast_mode/observatory/ai_consultation/ui/DoctorStatusIndicator';

// Mock fetch
global.fetch = jest.fn();

// Create theme for testing
const theme = createTheme();

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

// Mock data
const mockDoctorStatus: DoctorStatus = {
  isAvailable: true,
  currentLoad: 25,
  maxCapacity: 100,
  averageResponseTime: 2.5,
  totalConsultations: 150,
  costToday: 12.50,
  lastUpdated: '2024-01-15T10:30:00Z',
  healthStatus: 'healthy',
  message: 'All systems operational'
};

const mockUnavailableStatus: DoctorStatus = {
  isAvailable: false,
  currentLoad: 0,
  maxCapacity: 100,
  averageResponseTime: 0,
  totalConsultations: 150,
  costToday: 12.50,
  lastUpdated: '2024-01-15T10:30:00Z',
  healthStatus: 'critical',
  message: 'System maintenance in progress'
};

describe('DoctorStatusIndicator', () => {
  let server: WS;

  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as jest.Mock).mockClear();
    
    // Create WebSocket mock server
    server = new WS('ws://localhost/ws/doctor-status');
  });

  afterEach(() => {
    WS.clean();
    jest.clearAllTimers();
  });

  describe('Feature Flag Behavior', () => {
    it('should not render when disabled', () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator enabled={false} />
        </TestWrapper>
      );

      expect(screen.queryByText(/doctor/i)).not.toBeInTheDocument();
    });

    it('should render when enabled', async () => {
      // Mock successful fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator enabled={true} />
        </TestWrapper>
      );

      // Should show loading initially
      expect(screen.getByText(/loading doctor status/i)).toBeInTheDocument();

      // Wait for status to load
      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner initially', () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      expect(screen.getByText(/loading doctor status/i)).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should show error state when fetch fails', async () => {
      // Mock fetch failure
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/status unavailable/i)).toBeInTheDocument();
      });
    });
  });

  describe('Status Display', () => {
    it('should display available status correctly', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator showDetails={true} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
        expect(screen.getByText(/load: 25\/100/i)).toBeInTheDocument();
        expect(screen.getByText(/avg: 2\.5s/i)).toBeInTheDocument();
        expect(screen.getByText(/total: 150/i)).toBeInTheDocument();
      });
    });

    it('should display unavailable status correctly', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUnavailableStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator showDetails={true} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/doctor is out/i)).toBeInTheDocument();
        expect(screen.getByText(/system maintenance in progress/i)).toBeInTheDocument();
      });
    });

    it('should show health warnings for degraded status', async () => {
      const degradedStatus = {
        ...mockDoctorStatus,
        healthStatus: 'degraded' as const
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => degradedStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
        // Should show warning icon for degraded health
        expect(screen.getByTestId('WarningIcon')).toBeInTheDocument();
      });
    });
  });

  describe('Compact Mode', () => {
    it('should render compact version', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator compact={true} />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should not show text in compact mode
        expect(screen.queryByText(/doctor is in/i)).not.toBeInTheDocument();
        // Should show icon
        expect(screen.getByTestId('MedicalServicesIcon')).toBeInTheDocument();
      });
    });

    it('should show tooltip in compact mode', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator compact={true} />
        </TestWrapper>
      );

      await waitFor(() => {
        const icon = screen.getByTestId('MedicalServicesIcon');
        fireEvent.mouseOver(icon);
      });

      await waitFor(() => {
        expect(screen.getByText(/doctor is available/i)).toBeInTheDocument();
        expect(screen.getByText(/load: 25\/100/i)).toBeInTheDocument();
      });
    });
  });

  describe('WebSocket Integration', () => {
    it('should connect to WebSocket and receive status updates', async () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator websocketUrl="/ws/doctor-status" />
        </TestWrapper>
      );

      // Wait for WebSocket connection
      await server.connected;

      // Send status update
      act(() => {
        server.send(JSON.stringify({
          type: 'status_update',
          status: mockDoctorStatus
        }));
      });

      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });
    });

    it('should handle WebSocket connection failures gracefully', async () => {
      // Mock fetch as fallback
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator websocketUrl="/invalid-ws-url" />
        </TestWrapper>
      );

      // Should fallback to polling
      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });
    });

    it('should send ping/pong messages', async () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await server.connected;

      // Send initial status
      act(() => {
        server.send(JSON.stringify({
          type: 'status_update',
          status: mockDoctorStatus
        }));
      });

      // Simulate client sending ping
      act(() => {
        server.send(JSON.stringify({ type: 'ping' }));
      });

      // Should receive pong response
      await expect(server).toReceiveMessage(
        JSON.stringify({ type: 'pong', timestamp: expect.any(String) })
      );
    });
  });

  describe('Polling Fallback', () => {
    it('should use polling when WebSocket is disabled', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDoctorStatus
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockDoctorStatus, currentLoad: 30 })
        });

      render(
        <TestWrapper>
          <DoctorStatusIndicator pollingInterval={100} />
        </TestWrapper>
      );

      // Initial fetch
      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });

      // Wait for polling interval
      await act(async () => {
        jest.advanceTimersByTime(100);
      });

      // Should have made multiple fetch calls
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('should handle polling errors gracefully', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDoctorStatus
        })
        .mockRejectedValueOnce(new Error('Network error'));

      const onError = jest.fn();

      render(
        <TestWrapper>
          <DoctorStatusIndicator pollingInterval={100} onError={onError} />
        </TestWrapper>
      );

      // Initial successful fetch
      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });

      // Wait for polling interval with error
      await act(async () => {
        jest.advanceTimersByTime(100);
      });

      // Should call error callback
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(expect.any(Error));
      });
    });
  });

  describe('User Interactions', () => {
    it('should refresh status when refresh button is clicked', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDoctorStatus
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockDoctorStatus, currentLoad: 50 })
        });

      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
      });

      // Click refresh button
      const refreshButton = screen.getByLabelText(/refresh status/i);
      fireEvent.click(refreshButton);

      // Should make another fetch call
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should call onStatusChange callback when status updates', async () => {
      const onStatusChange = jest.fn();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator onStatusChange={onStatusChange} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(onStatusChange).toHaveBeenCalledWith(mockDoctorStatus);
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error snackbar for connection failures', async () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator websocketUrl="/failing-ws" />
        </TestWrapper>
      );

      // Simulate WebSocket connection failure
      await act(async () => {
        server.error();
      });

      await waitFor(() => {
        expect(screen.getByText(/doctor status service temporarily unavailable/i)).toBeInTheDocument();
      });
    });

    it('should handle malformed WebSocket messages', async () => {
      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await server.connected;

      // Send malformed JSON
      act(() => {
        server.send('invalid json');
      });

      // Should not crash the component
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByLabelText(/refresh status/i)).toBeInTheDocument();
      });
    });

    it('should support keyboard navigation', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDoctorStatus
      });

      render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await waitFor(() => {
        const refreshButton = screen.getByLabelText(/refresh status/i);
        expect(refreshButton).toBeInTheDocument();
        
        // Should be focusable
        refreshButton.focus();
        expect(refreshButton).toHaveFocus();
      });
    });
  });

  describe('Performance', () => {
    it('should cleanup WebSocket connection on unmount', async () => {
      const { unmount } = render(
        <TestWrapper>
          <DoctorStatusIndicator />
        </TestWrapper>
      );

      await server.connected;

      // Unmount component
      unmount();

      // WebSocket should be closed
      await server.closed;
    });

    it('should cleanup polling interval on unmount', async () => {
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

      const { unmount } = render(
        <TestWrapper>
          <DoctorStatusIndicator pollingInterval={1000} />
        </TestWrapper>
      );

      unmount();

      expect(clearIntervalSpy).toHaveBeenCalled();
    });
  });
});

describe('DoctorStatusIndicator Integration', () => {
  it('should work with real WebSocket server', async () => {
    // This would be an integration test with actual WebSocket server
    // For now, we'll simulate the integration
    
    const server = new WS('ws://localhost:8000/ws/doctor-status');
    
    render(
      <TestWrapper>
        <DoctorStatusIndicator websocketUrl="ws://localhost:8000/ws/doctor-status" />
      </TestWrapper>
    );

    await server.connected;

    // Simulate server sending status update
    act(() => {
      server.send(JSON.stringify({
        type: 'status_update',
        status: mockDoctorStatus
      }));
    });

    await waitFor(() => {
      expect(screen.getByText(/doctor is in/i)).toBeInTheDocument();
    });

    server.close();
  });
});