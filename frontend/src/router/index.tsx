import { createBrowserRouter } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import Home from '../pages/Home'
import Catalog from '../pages/Catalog'
import NotFound from '../pages/NotFound'
import Login from '../pages/Login'
import Register from '../pages/Register'
import PasswordReset from '../pages/PasswordReset'
import PasswordResetConfirm from '../pages/PasswordResetConfirm'
import ExcursionDetail from '../pages/ExcursionDetail'
import Booking from '../pages/Booking'
import Account from '../pages/Account'
import Certificates from '../pages/Certificates'
import News from '../pages/News'
import RecommendationInfo from '../pages/RecommendationInfo'
import { ProtectedRoute } from '../routes/ProtectedRoute'

export const router = createBrowserRouter([
    {
        path: '/',
        element: <MainLayout />,
        errorElement: <NotFound />,
        children: [
            {
                index: true,
                element: <Home />,
            },
            {
                path: 'catalog',
                element: <Catalog />,
            },
            {
                path: 'excursion/:slug',
                element: <ExcursionDetail />,
            },
            {
                path: 'booking/:excursionId/:slotId',
                element: (
                    <ProtectedRoute>
                        <Booking />
                    </ProtectedRoute>
                ),
            },
            {
                path: 'account',
                element: (
                    <ProtectedRoute>
                        <Account />
                    </ProtectedRoute>
                ),
            },
            {
                path: 'certificates',
                element: <Certificates />,
            },
            {
                path: 'news',
                element: <News />,
            },
            {
                path: 'recommendations',
                element: <RecommendationInfo />,
            },
        ],
    },
    {
        path: '/login',
        element: <Login />,
    },
    {
        path: '/register',
        element: <Register />,
    },
    {
        path: '/password-reset',
        element: <PasswordReset />,
    },
    {
        path: '/password-reset/:uidb64/:token',
        element: <PasswordResetConfirm />,
    },
])
