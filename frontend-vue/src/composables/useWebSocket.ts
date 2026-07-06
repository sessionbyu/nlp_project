/**
 * WebSocket 连接管理
 *
 * 功能：
 * 1. 连接/断开 WebSocket
 * 2. JWT 认证
 * 3. 消息订阅和处理
 * 4. 心跳检测
 * 5. 自动重连
 */

import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { WebSocketMessage } from '@/types/websocket'

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnected?: (connectionId: string) => void
  onDisconnected?: () => void
  onError?: (error: Event) => void
  autoReconnect?: boolean
  reconnectInterval?: number
}

export function useWebSocket(taskId: string, options: UseWebSocketOptions = {}) {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const connectionId = ref<string>('')
  const error = ref<string>('')
  const authStore = useAuthStore()

  const {
    onMessage,
    onConnected,
    onDisconnected,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options

  // 连接 WebSocket
  const connect = () => {
    if (!authStore.token) {
      error.value = '未登录，无法建立 WebSocket 连接'
      return
    }

    // 关闭现有连接
    if (ws.value) {
      ws.value.close()
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/v1/ws/${taskId}?token=${authStore.token}`

      ws.value = new WebSocket(wsUrl)

      // 连接成功
      ws.value.onopen = () => {
        console.log('WebSocket 连接成功')
        isConnected.value = true
        error.value = ''
      }

      // 接收消息
      ws.value.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket 消息:', data)

          // 处理连接成功
          if (data.type === 'connected') {
            connectionId.value = data.connection_id || ''
            onConnected?.(connectionId.value)
          }
          // 处理错误
          else if (data.type === 'error') {
            error.value = data.message || 'WebSocket 错误'
            onError?.(new Event('error'))
          }
          // 处理其他消息
          else {
            onMessage?.(data)
          }
        } catch (e) {
          console.error('解析 WebSocket 消息失败:', e)
        }
      }

      // 连接关闭
      ws.value.onclose = (event) => {
        console.log('WebSocket 连接关闭:', event.code, event.reason)
        isConnected.value = false
        ws.value = null
        onDisconnected?.()

        // 自动重连
        if (autoReconnect && !event.wasClean) {
          console.log(`${reconnectInterval}ms 后尝试重连...`)
          setTimeout(connect, reconnectInterval)
        }
      }

      // 连接错误
      ws.value.onerror = (event) => {
        console.error('WebSocket 错误:', event)
        error.value = 'WebSocket 连接失败'
        onError?.(event)
      }
    } catch (e) {
      console.error('创建 WebSocket 失败:', e)
      error.value = '创建 WebSocket 失败'
    }
  }

  // 断开连接
  const disconnect = () => {
    if (ws.value) {
      ws.value.close(1000, '正常关闭')
      ws.value = null
    }
    isConnected.value = false
    connectionId.value = ''
  }

  // 发送消息
  const send = (data: any) => {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    connectionId,
    error,
    connect,
    disconnect,
    send,
  }
}
