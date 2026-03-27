import { Container } from 'react-bootstrap'

export default function Home() {
    return (
        <>
            <section className='bg-primary text-white text-center py-5'>
                <Container>
                    <h1 className='display-4 fw-bold'>
                        Добро пожаловать в мир путешествий!
                    </h1>
                    <p className='lead'>Лучшие экскурсии по Омску и области</p>
                </Container>
            </section>

            <Container className='py-5'>
                <h2 className='text-center mb-5'>Что дальше?</h2>
                <p className='text-center'>
                    Пока здесь заглушка. Следующий шаг — hero + ближайшие туры.
                </p>
            </Container>
        </>
    )
}
