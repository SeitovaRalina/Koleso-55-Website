import { Link } from 'react-router-dom'
import CustomRequest from '../components/home/CustomRequest'
import { CONTACTS } from '../config/contacts'

const pageClass = 'mx-auto max-w-content px-4 py-12 text-neutral-ink'

export function About() {
  return <section className={pageClass}><h1 className='text-4xl font-bold'>О компании</h1><p className='mt-5 max-w-2xl leading-7 text-neutral-text'>«Колесо путешествий 55» организует экскурсии по Омску, области и России. Помогаем выбрать маршрут, дату и формат поездки.</p><Link className='mt-6 inline-flex text-brand-deep hover:underline' to='/contacts'>Связаться с нами</Link></section>
}

export function Contacts() {
  return <section className={pageClass}><h1 className='text-4xl font-bold'>Контакты</h1><div className='mt-6 grid gap-3 text-neutral-text'>{CONTACTS.phones.map(phone => <a key={phone.raw} href={`tel:${phone.raw}`} className='hover:text-brand-deep'>{phone.name}: {phone.label}</a>)}<a href={`mailto:${CONTACTS.email}`} className='hover:text-brand-deep'>{CONTACTS.email}</a></div></section>
}

export function Faq() {
  const questions = [['Как оставить заявку на экскурсию?', 'Выберите программу и дату, укажите ФИО и телефон. Аккаунт не нужен. Менеджер свяжется с вами.'], ['Когда участие подтверждено?', 'После связи с менеджером и согласования деталей. Отправка заявки не занимает место автоматически.'], ['Как отменить заявку?', 'Сообщите менеджеру об отмене. Если заявка видна в личном кабинете, её также можно отменить там, пока она новая или подтверждённая.']]
  return <section className={pageClass}><h1 className='text-4xl font-bold'>Частые вопросы</h1><div className='mt-8 grid gap-4'>{questions.map(([question, answer]) => <details key={question} className='rounded-card border border-neutral-line bg-white p-5'><summary className='cursor-pointer font-bold'>{question}</summary><p className='mt-3 text-neutral-text'>{answer}</p></details>)}</div></section>
}

export function BookingRules() {
  return <section className={pageClass}><h1 className='text-4xl font-bold'>Правила бронирования</h1><ul className='mt-6 list-disc space-y-3 pl-5 text-neutral-text'><li>Выберите программу и дату, укажите ФИО и телефон, отправьте заявку. Аккаунт не нужен.</li><li>Менеджер свяжется с вами, уточнит стоимость и доступность.</li><li>Отправка заявки не подтверждает участие и не занимает место автоматически.</li><li>Онлайн-оплата сейчас недоступна; условия согласуются с менеджером.</li></ul></section>
}

export function Activities() {
  return <section className={pageClass}><h1 className='text-4xl font-bold'>Афиша активностей</h1><p className='mt-5 max-w-2xl text-neutral-text'>Выбирайте ближайшие экскурсии и события по дате, месту и стоимости.</p><Link to='/catalog' className='mt-6 inline-flex rounded-card bg-brand-deep px-5 py-3 font-semibold text-white hover:bg-brand-sky'>Открыть афишу</Link></section>
}

export function CustomTour() {
  return <><div className={pageClass}><h1 className='text-4xl font-bold'>Экскурсия на заказ</h1><p className='mt-4 text-neutral-text'>Расскажите о маршруте, датах и составе группы. Менеджер подготовит предложение.</p></div><CustomRequest /></>
}

export function LegalPage({ type }: { type: 'consent' | 'policy' }) {
  const isConsent = type === 'consent'
  const title = isConsent ? 'Согласие на обработку персональных данных' : 'Политика конфиденциальности'
  const document = isConsent ? '/documents/Согласие_туриста_или_иного_заказчика_ТП_на_обработку_ПД_.docx' : '/documents/Политика_в_отношении_обработки_персональных_данных.docx'
  return <section className={pageClass}><h1 className='text-4xl font-bold'>{title}</h1><p className='mt-5 max-w-2xl leading-7 text-neutral-text'>Полный документ доступен для скачивания. Перед регистрацией и бронированием пользователь подтверждает ознакомление с условиями.</p><a href={document} download className='mt-6 inline-flex rounded-card border border-brand-deep px-5 py-3 font-semibold text-brand-deep hover:bg-brand-mist'>Скачать документ</a></section>
}
