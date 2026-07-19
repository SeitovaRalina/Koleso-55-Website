import { Link } from 'react-router-dom'

export default function GiftCertificates() {
  return (
    <section className='py-16 px-4 bg-gradient-to-r from-primary to-blue-600 text-white'>
      <div className='max-w-6xl mx-auto'>
        <div className='flex flex-col md:flex-row items-center gap-12'>
          <div className='w-full md:w-1/2'>
            <h2 className='text-3xl font-bold mb-4'>Подарите путешествие</h2>
            <p className='text-xl mb-8 text-blue-100'>
              Подарочные сертификаты на экскурсии — идеальный подарок для любого
              праздника
            </p>

            <div className='grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8'>
              {[
                { amount: '1000', title: 'Базовый' },
                { amount: '3000', title: 'Стандарт' },
                { amount: '5000', title: 'Премиум' },
              ].map(cert => (
                <div
                  key={cert.amount}
                  className='bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 text-center'
                >
                  <span className='text-3xl font-bold'>{cert.amount} ₽</span>
                  <p className='mt-1 text-blue-100 text-sm'>{cert.title}</p>
                </div>
              ))}
            </div>

            <Link
              to='/certificates'
              className='inline-block bg-white text-primary font-semibold py-3 px-8 rounded-lg hover:bg-blue-50 transition-colors'
            >
              Выбрать сертификат
            </Link>
          </div>

          <div className='w-full md:w-1/2 flex justify-center'>
            <img
              src='/certificate.jpg'
              alt='Подарочный сертификат'
              className='max-w-md w-auto h-auto rounded-xl shadow-2xl'
            />
          </div>
        </div>
      </div>
    </section>
  )
}
