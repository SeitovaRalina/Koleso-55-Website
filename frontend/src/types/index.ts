export interface Category {
  id: number
  name: string
  slug: string
}

export interface Excursion {
  id: number
  slug: string
  title: string
  short_description?: string
  description?: string
  category: Category
  location_type_display: string
  price: string
  duration: number
  average_rating: number | null
  review_count: number
  main_image: string | null
  images?: ExcursionImage[]
  slots?: ExcursionSlot[]
  is_active?: boolean
  approved_reviews?: Review[]
}

export interface ExcursionImage {
  id: number
  image: string
  alt_text: string
  is_main: boolean
}

export interface ReviewImage {
  id: number
  image: string
}

export interface ExcursionSlot {
  id: number
  date: string
  time: string
  max_participants: number
  available_seats: number
  is_available: boolean
  price_override?: string | null
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface Review {
  id: number
  excursion_id: number
  user_name: string
  rating: number
  text: string
  images?: ReviewImage[]
  created_at: string
  status?: 'pending' | 'approved' | 'rejected'
}

export interface Booking {
  id: number
  excursion_title: string
  slot_datetime: string
  num_participants: number
  status: 'new' | 'confirmed' | 'paid' | 'cancelled' | 'completed'
  status_display: string
  created_at: string
  contact_method_display: string
}

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  patronymic?: string
  phone: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface Recommendation {
  excursion_id: number
  score: number
  excursion?: Excursion
}

export interface LoginRequest {
  email_or_phone: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface RegisterRequest {
  email: string
  phone?: string
  password: string
  password2: string
}

export interface RegisterResponse {
  access: string
  refresh: string
  user: User
}

export interface ExcursionView {
  id: number
  excursion: number
  excursion_title: string
  user?: number
  user_email?: string
  session_id?: string
  started_at: string
  duration: number
}

export interface Wishlist {
  id: number
  excursion: Excursion
  added_at: string // Use a more specific type if possible
}
