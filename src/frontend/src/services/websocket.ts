/**
 * WebSocket service for real-time simulation updates
 *
 * Manages WebSocket connections to receive live progress updates.
 */

import type { WebSocketMessage, ProgressUpdate } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export type MessageHandler = (message: WebSocketMessage) => void

export class SimulationWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Set<MessageHandler> = new Set()
  private simulationId: string

  constructor(simulationId: string) {
    this.simulationId = simulationId
  }

  /**
   * Connect to WebSocket
   */
  connect(): void {
    const url = `${WS_URL}/api/simulations/${this.simulationId}/progress`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log(`WebSocket connected for simulation ${this.simulationId}`)
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        this.messageHandlers.forEach((handler) => handler(message))
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket closed')

      // Attempt reconnection
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)

        setTimeout(() => {
          this.connect()
        }, this.reconnectDelay * this.reconnectAttempts)
      }
    }
  }

  /**
   * Add message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler)

    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler)
    }
  }

  /**
   * Send ping to keep connection alive
   */
  ping(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send('ping')
    }
  }

  /**
   * Close WebSocket connection
   */
  close(): void {
    this.maxReconnectAttempts = 0 // Prevent reconnection
    this.ws?.close()
    this.ws = null
    this.messageHandlers.clear()
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

/**
 * React hook for WebSocket connection
 */
export function useSimulationWebSocket(
  simulationId: string,
  onProgress?: (update: ProgressUpdate) => void
) {
  const wsRef = React.useRef<SimulationWebSocket | null>(null)

  React.useEffect(() => {
    if (!simulationId) return

    // Create and connect WebSocket
    const ws = new SimulationWebSocket(simulationId)
    wsRef.current = ws

    // Add message handler
    const unsubscribe = ws.onMessage((message) => {
      if (message.type === 'progress' && onProgress) {
        onProgress(message)
      }
    })

    // Connect
    ws.connect()

    // Ping every 25 seconds to keep alive
    const pingInterval = setInterval(() => {
      ws.ping()
    }, 25000)

    // Cleanup
    return () => {
      clearInterval(pingInterval)
      unsubscribe()
      ws.close()
    }
  }, [simulationId, onProgress])

  return wsRef.current
}

// Import React for the hook
import React from 'react'
