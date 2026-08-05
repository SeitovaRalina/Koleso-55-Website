import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { ScrollToTop } from '../ScrollToTop'

export default function RootLayout() {
  const { pathname } = useLocation()

  useEffect(() => {
    const titles: Record<string, string> = {
      '/': 'Экскурсии в Омске',
      '/catalog': 'Каталог экскурсий',
      '/certificates': 'Подарочные сертификаты',
      '/news': 'Новости',
      '/recommendations': 'Рекомендации',
      '/about': 'О компании',
      '/contacts': 'Контакты',
      '/faq': 'Частые вопросы',
      '/booking': 'Правила бронирования',
      '/activities': 'Афиша активностей',
      '/custom-tour': 'Экскурсия на заказ',
      '/login': 'Вход',
      '/register': 'Регистрация',
      '/account': 'Личный кабинет',
      '/legal/personal-data': 'Согласие на обработку данных',
      '/legal/privacy-policy': 'Политика конфиденциальности',
    }
    const title = pathname.startsWith('/excursion/') ? 'Экскурсия' : titles[pathname] || 'Колесо путешествий 55'
    document.title = `${title} | Колесо путешествий 55`
  }, [pathname])

  return (
    <>
      <ScrollToTop />
      <Outlet />
    </>
  )
}
