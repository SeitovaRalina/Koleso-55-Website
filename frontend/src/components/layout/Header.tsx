import { useState, type FormEvent } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const navigate = useNavigate()

    const handleSearch = (e: FormEvent) => {
        e.preventDefault()
        if (searchQuery.trim()) {
            navigate(`/catalog?search=${encodeURIComponent(searchQuery.trim())}`)
        }
    }

    return (
        <header className='bg-white shadow-sm sticky top-0 z-50'>
            <div className='max-w-6xl mx-auto px-4'>
                <div className='flex items-center justify-between h-16'>
                    <Link to='/' className='flex items-center gap-3'>
                        <img
                            src='/logo.png'
                            alt='КОЛЕСО путешествий 55'
                            className='h-10 w-auto'
                        />
                    </Link>

                    <nav className='hidden md:flex items-center gap-6'>
                        <NavLink
                            to='/'
                            end
                            className={({ isActive }) =>
                                `text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                        >
                            Главная
                        </NavLink>
                        <NavLink
                            to='/catalog'
                            className={({ isActive }) =>
                                `text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                        >
                            Экскурсии
                        </NavLink>
                        <NavLink
                            to='/certificates'
                            className={({ isActive }) =>
                                `text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                        >
                            Сертификаты
                        </NavLink>
                        <NavLink
                            to='/account'
                            className={({ isActive }) =>
                                `text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                        >
                            Личный кабинет
                        </NavLink>
                    </nav>

                    <div className='hidden md:flex items-center gap-4'>
                        <form onSubmit={handleSearch} className='relative'>
                            <input
                                type='text'
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder='Поиск экскурсий...'
                                className='w-64 px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
                            />
                            <svg
                                className='w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400'
                                fill='none'
                                stroke='currentColor'
                                viewBox='0 0 24 24'
                            >
                                <path
                                    strokeLinecap='round'
                                    strokeLinejoin='round'
                                    strokeWidth={2}
                                    d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
                                />
                            </svg>
                        </form>
                    </div>

                    <button
                        className='md:hidden p-2'
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                    >
                        <svg
                            className='w-6 h-6'
                            fill='none'
                            stroke='currentColor'
                            viewBox='0 0 24 24'
                        >
                            {isMenuOpen ? (
                                <path
                                    strokeLinecap='round'
                                    strokeLinejoin='round'
                                    strokeWidth={2}
                                    d='M6 18L18 6M6 6l12 12'
                                />
                            ) : (
                                <path
                                    strokeLinecap='round'
                                    strokeLinejoin='round'
                                    strokeWidth={2}
                                    d='M4 6h16M4 12h16M4 18h16'
                                />
                            )}
                        </svg>
                    </button>
                </div>

                {isMenuOpen && (
                    <nav className='md:hidden py-4 border-t'>
                        <NavLink
                            to='/'
                            end
                            className={({ isActive }) =>
                                `block py-2 text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Главная
                        </NavLink>
                        <NavLink
                            to='/catalog'
                            className={({ isActive }) =>
                                `block py-2 text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Экскурсии
                        </NavLink>
                        <NavLink
                            to='/certificates'
                            className={({ isActive }) =>
                                `block py-2 text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Сертификаты
                        </NavLink>
                        <NavLink
                            to='/account'
                            className={({ isActive }) =>
                                `block py-2 text-gray-700 hover:text-primary transition-colors ${isActive ? 'text-primary font-semibold' : ''}`
                            }
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Личный кабинет
                        </NavLink>
                        <form onSubmit={handleSearch} className='mt-4'>
                            <input
                                type='text'
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder='Поиск экскурсий...'
                                className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
                            />
                        </form>
                    </nav>
                )}
            </div>
        </header>
    )
}
