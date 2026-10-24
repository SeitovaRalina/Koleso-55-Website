import { Link } from 'react-router-dom'

const directions = [
  {
    title: 'Экскурсии и путешествия',
    text: 'Знакомим с Омском и Омской областью, организуем поездки по России — для одного человека или группы.',
  },
  {
    title: 'Для детей и школьных групп',
    text: 'Подбираем познавательные экскурсии, поездки и мастер-классы с учётом возраста и интересов участников.',
  },
  {
    title: 'Активные и корпоративные программы',
    text: 'Помогаем провести совместный выезд, активный день или программу для команды.',
  },
]

export default function About() {
  return (
    <div className='text-neutral-ink'>
      <section className='bg-heritage-cream py-12 sm:py-16'>
        <div className='mx-auto max-w-content px-4'>
          <p className='text-sm font-semibold uppercase tracking-wider text-brand-deep'>О компании</p>
          <h1 className='mt-4 max-w-3xl text-3xl font-bold leading-tight sm:text-5xl'>
            Путешествия, которые подходят именно вам
          </h1>
          <p className='mt-6 max-w-2xl text-base leading-7 text-neutral-text sm:text-lg'>
            «Колесо путешествий 55» организует экскурсии и авторские программы по Омску,
            Омской области и России. Мы работаем с частными гостями, школьными группами
            и организациями.
          </p>
        </div>
      </section>

      <section className='mx-auto max-w-content px-4 py-12 sm:py-16'>
        <h2 className='text-2xl font-bold sm:text-3xl'>Что мы организуем</h2>
        <div className='mt-8 grid gap-6 md:grid-cols-3'>
          {directions.map(({ title, text }) => (
            <article key={title} className='border-t-2 border-brand-sky pt-5'>
              <h3 className='text-xl font-semibold'>{title}</h3>
              <p className='mt-3 leading-7 text-neutral-text'>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className='bg-brand-mist/50 py-12 sm:py-16'>
        <div className='mx-auto grid max-w-content gap-8 px-4 md:grid-cols-[1fr_auto] md:items-center'>
          <div>
            <h2 className='text-2xl font-bold sm:text-3xl'>Поездка под ваш запрос</h2>
            <p className='mt-4 max-w-2xl leading-7 text-neutral-text'>
              Расскажите, куда хотите отправиться, с кем и в каком формате. Обсудим программу
              и условия. Работаем с физическими и юридическими лицами, оформляем договоры
              и предоставляем отчётные документы.
            </p>
          </div>
          <Link to='/contacts' className='inline-flex min-h-11 items-center justify-center rounded-card bg-brand-deep px-6 py-3 font-semibold text-white hover:bg-brand-sky'>
            Связаться с нами
          </Link>
        </div>
      </section>
    </div>
  )
}
