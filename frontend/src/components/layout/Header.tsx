import { Navbar, Container, Nav } from 'react-bootstrap'
import { NavLink } from 'react-router-dom'

export default function Header() {
    return (
        <Navbar bg='dark' variant='dark' expand='lg' sticky='top'>
            <Container>
                <Navbar.Brand as={NavLink} to='/'>
                    КОЛЕСО путешествий 55
                </Navbar.Brand>

                <Navbar.Toggle aria-controls='basic-navbar-nav' />

                <Navbar.Collapse id='basic-navbar-nav'>
                    <Nav className='ms-auto'>
                        <Nav.Link as={NavLink} to='/' end>
                            Главная
                        </Nav.Link>
                        <Nav.Link as={NavLink} to='/catalog'>
                            Экскурсии
                        </Nav.Link>
                        <Nav.Link as={NavLink} to='/cart'>
                            Корзина
                        </Nav.Link>
                        <Nav.Link as={NavLink} to='/login'>
                            Войти
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    )
}
