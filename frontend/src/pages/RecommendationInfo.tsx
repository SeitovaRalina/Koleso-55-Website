import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/useAuth'

export default function RecommendationInfo() {
  const { isAuthenticated } = useAuth()
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Как работают рекомендации</h1>

        <div className="bg-white rounded-lg shadow-md p-8 space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Персональные рекомендации</h2>
            <p className="text-gray-700 mb-4">
              Наша система анализирует ваши интересы и историю просмотров, чтобы предложить вам экскурсии, которые вам наверняка понравятся.
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>Мы отслеживаем, какие экскурсии вы просматриваете</li>
              <li>Анализируем ваши бронирования</li>
              <li>Учитываем ваши предпочтения по категориям и локациям</li>
              <li>Предлагаем похожие экскурсии на основе ваших интересов</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Похожие экскурсии</h2>
            <p className="text-gray-700 mb-4">
              На странице каждой экскурсии мы показываем похожие варианты, основываясь на:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>Категории экскурсии</li>
              <li>Типу локации (городские, загородные, туры по России)</li>
              <li>Ценовому диапазону</li>
              <li>Длительности</li>
              <li>Популярности среди других пользователей</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Конфиденциальность</h2>
            <p className="text-gray-700">
              Мы ценим вашу приватность. Все данные о ваших просмотрах и предпочтениях используются исключительно для улучшения качества рекомендаций и не передаются третьим лицам.
            </p>
          </section>

          <section className="bg-blue-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2">Хотите улучшить рекомендации?</h2>
            <p className="text-gray-700 mb-4">
              Войдите в аккаунт, чтобы система могла запоминать ваши предпочтения и предлагать более релевантные экскурсии.
            </p>
            <Link to={isAuthenticated ? '/account?tab=recommendations' : '/login'} className="inline-flex bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
              {isAuthenticated ? 'Открыть мои рекомендации' : 'Войти в аккаунт'}
            </Link>
          </section>
        </div>
      </div>
    </div>
  )
}
