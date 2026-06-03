import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Hero() {
  const navigate = useNavigate()
  const [destination, setDestination] = useState('')
  const [date, setDate] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (destination) params.append('search', destination)
    if (date) params.append('date', date)
    navigate(`/catalog?${params.toString()}`)
  }

  return (
    <section
      className='relative bg-cover bg-center bg-no-repeat py-32 px-4'
      style={{
        backgroundImage: 'url(/hero-bg.jpg)',
      }}
    >
      <div className='absolute inset-0 bg-black/40'></div>

      <div className='relative max-w-6xl mx-auto'>
        <div className='flex items-center'>
          <div className='w-full md:w-1/2'>
            <form
              onSubmit={handleSearch}
              className='bg-white rounded-2xl p-6 shadow-2xl max-w-md'
            >
              <div className='space-y-4'>
                <div>
                  <label className='block text-gray-700 text-sm font-medium mb-2'>
                    Куда хотите поехать?
                  </label>
                  <input
                    type='text'
                    value={destination}
                    onChange={e => setDestination(e.target.value)}
                    placeholder='Например: Омск, Тара'
                    className='w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary text-gray-900'
                  />
                </div>

                <div>
                  <label className='block text-gray-700 text-sm font-medium mb-2'>
                    Дата
                  </label>
                  <input
                    type='date'
                    value={date}
                    onChange={e => setDate(e.target.value)}
                    className='w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary text-gray-900'
                  />
                </div>

                <button
                  type='submit'
                  className='w-full bg-primary hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors'
                >
                  Найти экскурсии
                </button>
              </div>
            </form>
          </div>

          <div className='hidden md:block md:w-1/2'></div>
        </div>
      </div>
    </section>
  )
}
