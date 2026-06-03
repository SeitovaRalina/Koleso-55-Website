---
description: frontend
---
Create a production-ready frontend for "Колесо путешествий 55" travel excursion platform.

## Tech Stack
- React + TypeScript + Vite
- React Router + Tailwind CSS + shadcn/ui
- Axios + React Query + React Hook Form + Zod
- Framer Motion + Swiper.js
- Context API for auth
- JWT with refresh token

## Design Requirements
- Modern calm UI, soft shadows, rounded cards, clean typography
- Primary color: #2D60B3
- Responsive: desktop/tablet/mobile
- Hero sections only on homepage (optional per category page)
- Excursion cards: vertical 3:4 images, hover swaps to second photo
- Badge for category, favorite button overlay on image
- Skeleton loaders, loading/error/empty states

## Pages & Components

### 1. Homepage
Layout matches provided design:
- Hero: Title, subtitle, search bar (destination), date picker, CTA button
- Weekly events carousel (excursion cards)
- "How it works" - 3 steps: Choose → Book & Pay → Get confirmation
- Reviews section (testimonials carousel)
- Gift certificates CTA block
- "Not found what you're looking for?" - custom request form
- Footer: Client links, Company links, Contacts with 3 managers' phones

### 2. Catalog Page
Grid layout with sidebar filters:
- Category chips (Обзорные, Активные, Мастер-классы, Дегустации, Авторские)
- Active count: "Найдено X экскурсий"
- Filters: Price range, Location (Омск/Омская область/Россия), Duration (до 2ч/2-4ч/более 4ч), Date picker
- Sorting: Popular, Price asc/desc, Duration, Newest
- Pagination
- URL params sync for filters

### 3. Excursion Detail Page
- Vertical main image (3:4), gallery carousel
- Title, rating, price, duration, location type, category badge
- Full description
- Slot selection (date/time) with availability
- Booking widget (participants count)
- Favorite button
- Reviews section (with photos support)
- "You may also like" from `/api/v1/similar/{id}` endpoint
- Analytics tracking: view start/heartbeat/end

### 4. Booking Page
Multi-step or single form:
- Slot confirmation
- Personal data: first name, last name, patronymic, phone, email
- Participants count
- Communication method (call/WhatsApp/Telegram/email)
- Order summary
- Payment placeholder (ready for ЮKassa/Tinkoff integration)

### 5. User Account (Protected Route)
Tabs layout:
- Profile: Edit name, phone, patronymic (email readonly)
- Booking history: List with status badges (new/confirmed/paid/cancelled/completed), cancel action for new/confirmed
- Favorites: Grid of excursions, remove button
- Recommendations: List of personalized recommendations

### 6. Authentication
- Login: email/phone + password
- Registration: email, phone, password, confirm password
- Password reset flow
- OAuth: Google, VK
- Registration MUST include 2 checkboxes with links to legal docs:
  - "Согласие на обработку персональных данных"
  - "Политика обработки персональных данных"

### 7. Certificates Page
- Catalog of gift certificates (nominal values)
- Purchase form (buyer + recipient info)
- Digital/printed format choice

### 8. News/Events Page
- Blog-style grid for travel articles and announcements

### 9. Recommendation System Info Page
- Explain how personalized and similar recommendations work (user-friendly text)

## Backend Integration
Base API URL from env: `VITE_API_URL=http://localhost:8001/api`

### Axios Setup
- Base URL from env
- Request/response interceptors
- JWT refresh token interceptor (401 handling)
- Session ID management for anonymous users (generate UUID, store in localStorage)

## Folder Structure
src/
├── api/ # API services (auth, excursions, bookings, etc.)
├── components/ # Reusable UI (ExcursionCard, FilterSidebar, etc.)
├── contexts/ # AuthContext, CartContext
├── hooks/ # useAuth, useSession, useRecommendations
├── layouts/ # MainLayout, AuthLayout
├── pages/ # Home, Catalog, Detail, Booking, Account, etc.
├── routes/ # ProtectedRoute, PublicRoute
├── types/ # TypeScript interfaces
├── utils/ # helpers, formatters, validators
└── lib/ # shadcn/ui components

text

## React Query Configuration
- Stale time: excursions 5 min, recommendations 1 hour, similar 24 hours
- Invalidate queries after mutations (add to wishlist, book, cancel)
- Prefetch similar excursions on detail page

## Feature Placeholders (backend not ready)
- Payment integration: mock "Pay" button with console.log
- Gift certificates purchase: mock success notification
- Custom excursion request: POST to email endpoint (mock)

## Additional Requirements
- Dockerfile for frontend (nginx serving build)
- Environment variables example (.env.example)
- SEO-friendly with react-helmet-async
- Accessibility: ARIA labels, keyboard navigation
- shadcn/ui components: Button, Card, Dialog, Form, Input, Select, Tabs, Toast
