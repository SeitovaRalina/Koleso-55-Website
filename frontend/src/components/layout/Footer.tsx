import { Container } from 'react-bootstrap'

export default function Footer() {
    return (
        <footer className='bg-dark text-white py-4 mt-auto'>
            <Container className='text-center'>
                <p className='mb-0'>
                    &copy; {new Date().getFullYear()} КОЛЕСО путешествий 55. Все права
                    защищены.
                </p>
            </Container>
        </footer>
    )
}
