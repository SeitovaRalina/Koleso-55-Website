import { createBrowserRouter } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import RootLayout from '../components/layout/RootLayout'
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
import GoogleCallback from '../pages/GoogleCallback'
import { About, Activities, BookingRules, Contacts, CustomTour, Faq, LegalPage } from '../pages/PublicPages'
import { ProtectedRoute } from '../routes/ProtectedRoute'

const UiKit = import.meta.env.DEV ? lazy(() => import('../pages/UiKit')) : null

export const router = createBrowserRouter([
    {
        element: <RootLayout />,
        errorElement: <NotFound />,
        children: [
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
                path: 'excursion/:excursionId',
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
            { path: 'about', element: <About /> },
            { path: 'contacts', element: <Contacts /> },
            { path: 'faq', element: <Faq /> },
            { path: 'booking', element: <BookingRules /> },
            { path: 'activities', element: <Activities /> },
            { path: 'custom-tour', element: <CustomTour /> },
            { path: 'legal/personal-data', element: <LegalPage type='consent' /> },
            { path: 'legal/personal-data-consent', element: <LegalPage type='consent' /> },
            { path: 'legal/privacy-policy', element: <LegalPage type='policy' /> },
            { path: 'legal/personal-data-policy', element: <LegalPage type='policy' /> },
            ...(import.meta.env.DEV ? [{
                path: 'ui-kit',
                element: UiKit ? (
                    <Suspense fallback={null}>
                        <UiKit />
                    </Suspense>
                ) : null,
            }] : []),
                ],
            },
            {
                path: 'login',
                element: <Login />,
            },
            {
                path: 'register',
                element: <Register />,
            },
            {
                path: 'password-reset',
                element: <PasswordReset />,
            },
            {
                path: 'password-reset/:uidb64/:token',
                element: <PasswordResetConfirm />,
            },
            {
                path: 'google-callback',
                element: <GoogleCallback />,
            },
            {
                path: '*',
                element: <NotFound />,
            },
        ],
    },
])
