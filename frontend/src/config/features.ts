export const featureFlags = {
  vkAuth: import.meta.env.VITE_VK_AUTH_ENABLED === 'true',
} as const
