// Mock service worker setup for development
import { setupWorker } from 'msw'
import { authHandlers } from './handlers/auth'
import { analysisHandlers } from './handlers/analysis'
import { reportsHandlers } from './handlers/reports'

export const worker = setupWorker(...authHandlers, ...analysisHandlers, ...reportsHandlers)