import { useState, type FormEvent } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  const showSearch = location.pathname === '/'

  const handleSearch = (event: FormEvent) => {
    event.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/catalog?search=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <header className='sticky top-0 z-50 border-b border-neutral-line bg-white/95 backdrop-blur'>
      <div className='mx-auto max-w-content px-4'>
        <div className='flex h-16 items-center justify-between gap-4'>
          <div className='flex min-w-0 flex-1 items-center gap-4'>
            <Link to='/' className='flex shrink-0 items-center'>
              <img
                src='/logo.png'
                alt='Колесо путешествий 55'
                className='h-10 w-auto'
              />
            </Link>

            {showSearch && (
              <form onSubmit={handleSearch} className='relative hidden w-full max-w-xs md:block'>
                <input
                  type='search'
                  value={searchQuery}
                  onChange={event => setSearchQuery(event.target.value)}
                  placeholder='Найти экскурсию...'
                  className='h-10 w-full rounded-card border border-neutral-line bg-[#f3f6fb] py-2 pl-10 pr-3 text-sm text-neutral-ink outline-none transition focus:border-brand-sky focus:ring-2 focus:ring-brand-sky/20'
                />
                <svg
                  className='absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-text'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                  aria-hidden='true'
                >
                  <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' />
                </svg>
              </form>
            )}
          </div>

          <nav className='hidden items-center gap-6 md:flex'>
            <HeaderNavLink to='/catalog'>Каталог</HeaderNavLink>
            <HeaderNavLink to='/certificates'>Сертификаты</HeaderNavLink>
            <HeaderNavLink to='/news'>Новости</HeaderNavLink>
            <NavLink
              to='/account'
              aria-label='Личный кабинет'
              className={({ isActive }) =>
                `flex h-10 w-10 items-center justify-center rounded-card border transition ${
                  isActive
                    ? 'border-brand-deep bg-brand-deep text-white'
                    : 'border-neutral-line text-neutral-ink hover:border-brand-sky hover:text-brand-deep'
                }`
              }
            >
              <svg className='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24' aria-hidden='true'>
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M15.75 7.5a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.25a7.5 7.5 0 0115 0' />
              </svg>
            </NavLink>
          </nav>

          <button
            type='button'
            className='rounded-card border border-neutral-line p-2 md:hidden'
            onClick={() => setIsMenuOpen(value => !value)}
            aria-label='Открыть меню'
            aria-expanded={isMenuOpen}
          >
            <svg className='h-6 w-6' fill='none' stroke='currentColor' viewBox='0 0 24 24' aria-hidden='true'>
              {isMenuOpen ? (
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M6 18L18 6M6 6l12 12' />
              ) : (
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M4 6h16M4 12h16M4 18h16' />
              )}
            </svg>
          </button>
        </div>

        {isMenuOpen && (
          <div className='border-t border-neutral-line py-4 md:hidden'>
            {showSearch && (
              <form onSubmit={handleSearch} className='mb-4'>
                <input
                  type='search'
                  value={searchQuery}
                  onChange={event => setSearchQuery(event.target.value)}
                  placeholder='Найти экскурсию...'
                  className='h-10 w-full rounded-card border border-neutral-line bg-[#f3f6fb] px-3 text-sm outline-none focus:border-brand-sky focus:ring-2 focus:ring-brand-sky/20'
                />
              </form>
            )}
            <nav className='grid gap-3'>
              <MobileNavLink to='/catalog' onClick={() => setIsMenuOpen(false)}>Каталог</MobileNavLink>
              <MobileNavLink to='/certificates' onClick={() => setIsMenuOpen(false)}>Сертификаты</MobileNavLink>
              <MobileNavLink to='/news' onClick={() => setIsMenuOpen(false)}>Новости</MobileNavLink>
              <MobileNavLink to='/account' onClick={() => setIsMenuOpen(false)}>Личный кабинет</MobileNavLink>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

function HeaderNavLink({ to, children }: { to: string; children: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `text-sm font-semibold transition ${
          isActive ? 'text-brand-deep' : 'text-neutral-ink hover:text-brand-deep'
        }`
      }
    >
      {children}
    </NavLink>
  )
}

function MobileNavLink({ to, onClick, children }: { to: string; onClick: () => void; children: string }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `rounded-card px-3 py-2 text-sm font-semibold transition ${
          isActive ? 'bg-brand-mist text-brand-deep' : 'text-neutral-ink hover:bg-brand-mist'
        }`
      }
    >
      {children}
    </NavLink>
  )
}
