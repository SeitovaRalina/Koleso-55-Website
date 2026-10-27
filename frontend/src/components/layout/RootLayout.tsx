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
    const aboutDescription = 'Колесо путешествий 55 организует экскурсии по Омску, Омской области и России, программы для школьных и корпоративных групп, мастер-классы и поездки под запрос.'
    const defaultDescription = 'Колесо путешествий 55 — экскурсии, путешествия, мастер-классы и активные программы по Омску, Омской области и России. Индивидуальные и групповые поездки.'
    const description = pathname === '/about' ? aboutDescription : defaultDescription
    const setMeta = (selector: string, value: string) => {
      const meta = document.querySelector<HTMLMetaElement>(selector)
      if (meta) meta.content = value
    }
    setMeta('meta[name="description"]', description)
    setMeta('meta[property="og:title"]', document.title)
    setMeta('meta[property="og:description"]', description)
    setMeta('meta[property="og:url"]', `https://koleso-travel55.ru${pathname}`)
  }, [pathname])

  return (
    <>
      <ScrollToTop />
      <Outlet />
    </>
  )
}
