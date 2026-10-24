import { useEffect } from 'react'

export default function GoogleCallback() {
  useEffect(() => {
    // Получаем access_token из URL
    const urlParams = new URLSearchParams(window.location.hash.substring(1))
    const accessToken = urlParams.get('access_token')
    const provider = new URLSearchParams(window.location.search).get('provider') === 'vk' ? 'vk' : 'google'

    if (accessToken) {
      // Отправляем токен в родительское окно через postMessage
      window.opener.postMessage(
        { type: `${provider}_token`, token: accessToken },
        window.location.origin
      )
      // Родительское окно закроет popup после успешной обработки
    } else {
      // Если токена нет, отправляем ошибку
      window.opener.postMessage(
        { type: `${provider}_error`, error: 'No access token' },
        window.location.origin
      )
    }
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <p>Обработка авторизации...</p>
        <p className="text-sm text-gray-500 mt-2">Вы можете закрыть это окно</p>
      </div>
    </div>
  )
}
