const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

/**
 * Get base URL for media files (images, etc.)
 * Removes /api suffix from API_URL
 */
export function getMediaBaseUrl(): string {
  return API_URL.replace(/\/api$/, '')
}

/**
 * Get full URL for a media file path
 * @param path - Relative path from media root (e.g., /media/excursions/image.jpg)
 * @returns Full URL to the media file
 */
export function getMediaUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null
  }
  
  // If path is already a full URL, return it as is
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  
  // Otherwise, prepend the media base URL
  const baseUrl = getMediaBaseUrl()
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${baseUrl}${normalizedPath}`
}
