/**
 * WebSocket 消息类型定义
 */

export interface WebSocketMessage {
  type: string
  task_id?: string
  connection_id?: string
  current?: number
  total?: number
  progress_percent?: number
  notification_type?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  message?: string
  timestamp?: number
  error?: string
}

export interface WebSocketConnectedMessage extends WebSocketMessage {
  type: 'connected'
  connection_id: string
  task_id: string
}

export interface WebSocketProgressMessage extends WebSocketMessage {
  type: 'progress'
  task_id: string
  current: number
  total: number
  progress_percent: number
}

export interface WebSocketNotificationMessage extends WebSocketMessage {
  type: 'notification'
  notification_type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: number
}

export interface WebSocketPongMessage extends WebSocketMessage {
  type: 'pong'
  timestamp: number
}

export interface WebSocketErrorMessage extends WebSocketMessage {
  type: 'error'
  message: string
}

export type WebSocketMessageType =
  | WebSocketConnectedMessage
  | WebSocketProgressMessage
  | WebSocketNotificationMessage
  | WebSocketPongMessage
  | WebSocketErrorMessage
