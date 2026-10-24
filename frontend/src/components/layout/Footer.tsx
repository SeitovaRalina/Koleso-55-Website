import { Link } from 'react-router-dom'
import { CONTACTS, SOCIAL_LINKS } from '../../config/contacts'

const clientLinks = [
  ['Афиша активностей', '/activities'],
  ['Подарочные сертификаты', '/certificates'],
  ['Создать экскурсию на заказ', '/custom-tour'],
  ['Правила бронирования', '/booking'],
  ['Личный кабинет', '/account'],
  ['Частые вопросы', '/faq'],
]

const companyLinks = [
  ['О компании', '/about'],
  ['Новости', '/news'],
  ['Контакты', '/contacts'],
  ['Политика конфиденциальности', '/legal/privacy-policy'],
]

export default function Footer() {
  return <footer className='bg-[#dfe8f3] py-12 text-neutral-ink'><div className='mx-auto max-w-content px-4'><div className='grid gap-10 md:grid-cols-[1.25fr_1fr_1fr_1fr]'><div><Link to='/' className='inline-flex'><img src='/logo.png' alt='Колесо путешествий 55' className='h-16 w-auto' /></Link><p className='mt-5 max-w-sm text-sm leading-6 text-neutral-text'>Экскурсии и активный отдых в Омске и по России.</p></div><FooterColumn title='Клиентам' links={clientLinks} /><FooterColumn title='Компания' links={companyLinks} /><div><h3 className='text-sm font-bold'>Контакты</h3><div className='mt-4 grid gap-2 text-sm text-neutral-text'>{CONTACTS.phones.map(phone => <a key={phone.raw} href={`tel:${phone.raw}`} className='hover:text-brand-deep'>{phone.label}</a>)}<a href={`mailto:${CONTACTS.email}`} className='hover:text-brand-deep'>{CONTACTS.email}</a></div><div className='mt-6 flex flex-wrap gap-3'>{SOCIAL_LINKS.map(link => <a key={link.label} href={link.href} target='_blank' rel='noreferrer' aria-label={link.label} className='flex h-10 w-10 items-center justify-center rounded-card bg-brand-mist/75'><img src={link.icon} alt='' className='h-6 w-6' /></a>)}</div></div></div><div className='mt-10 border-t border-[#c6d3e3] pt-6 text-sm text-neutral-text'>© {new Date().getFullYear()} Колесо путешествий 55.</div></div></footer>
}

function FooterColumn({ title, links }: { title: string; links: string[][] }) {
  return <div><h3 className='text-sm font-bold'>{title}</h3><ul className='mt-4 space-y-2 text-sm text-neutral-text'>{links.map(([label, to]) => <li key={label}><Link to={to} className='hover:text-brand-deep'>{label}</Link></li>)}</ul></div>
}
