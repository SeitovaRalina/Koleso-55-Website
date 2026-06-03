import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false)

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
                    </nav>
                )}
            </div>
        </header>
    )
}
