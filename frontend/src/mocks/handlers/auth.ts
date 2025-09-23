// Mock handlers for authentication
import { rest } from 'msw'

export const authHandlers = [
  rest.post('/auth/login', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: {
          id: 1,
          name: 'Usuario Demo',
          email: 'demo@sentrix.com',
          role: 'user'
        },
        access_token: 'demo-token',
        refresh_token: 'demo-refresh-token'
      })
    )
  }),

  rest.post('/auth/register', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: {
          id: 1,
          name: 'Usuario Demo',
          email: 'demo@sentrix.com',
          role: 'user'
        },
        access_token: 'demo-token',
        refresh_token: 'demo-refresh-token'
      })
    )
  }),

  rest.get('/auth/profile', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        name: 'Usuario Demo',
        email: 'demo@sentrix.com',
        role: 'user'
      })
    )
  })
]