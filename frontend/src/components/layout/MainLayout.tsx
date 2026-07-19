import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import ChatAssistant from '../chat/ChatAssistant'

export default function MainLayout() {
    return (
        <div className='flex flex-col min-h-screen'>
            <Header />

            <main className='flex-grow'>
                <Outlet />
            </main>

            <Footer />
            <ChatAssistant />
        </div>
    )
}
