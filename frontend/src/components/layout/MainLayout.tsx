import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import { Container } from 'react-bootstrap'

export default function MainLayout() {
    return (
        <div className='d-flex flex-column min-vh-100'>
            <Header />

            <main className='flex-grow-1 py-4'>
                <Container>
                    <Outlet />
                </Container>
            </main>

            <Footer />
        </div>
    )
}
