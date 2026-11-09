import { useEffect, useState, type FormEvent } from 'react'
import { customTourRequestsApi } from '../../api/customTourRequests'
import { getApiErrorMessage } from '../../utils/apiError'
import { useAuth } from '../../contexts/useAuth'

export default function CustomRequest() {
  const { user } = useAuth()
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({ name: '', phone: '', email: '', description: '' })

  useEffect(() => {
    if (!user) return
    setFormData(current => ({ ...current,
      name: current.name || [user.last_name, user.first_name, user.patronymic].filter(Boolean).join(' '),
      phone: current.phone || user.phone || '', email: current.email || user.email || '',
    }))
  }, [user])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setStatus('')
    setIsSubmitting(true)
    try {
      await customTourRequestsApi.create(formData)
      setStatus('Заявка отправлена. Менеджер свяжется с вами.')
      setFormData({ name: '', phone: '', email: '', description: '' })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось отправить заявку. Попробуйте ещё раз.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className='bg-gray-50 px-4 py-16'>
      <div className='mx-auto max-w-3xl'>
        <h1 className='mb-4 text-center text-3xl font-bold'>Экскурсия на заказ</h1>
        <p className='mb-8 text-center text-gray-600'>Расскажите, куда хотите поехать, сколько вас и какие даты удобны. Менеджер подготовит предложение.</p>
        <form onSubmit={handleSubmit} className='rounded-card bg-white p-8 shadow-sm'>
          <div className='mb-6 grid grid-cols-1 gap-6 md:grid-cols-2'>
            <Field label='Ваше имя' required value={formData.name} onChange={value => setFormData({ ...formData, name: value })} placeholder='Иван Иванов' />
            <Field label='Телефон' type='tel' required value={formData.phone} onChange={value => setFormData({ ...formData, phone: value })} placeholder='+7 (999) 123-45-67' />
            <div className='md:col-span-2'><Field label='Email' type='email' value={formData.email} onChange={value => setFormData({ ...formData, email: value })} placeholder='example@mail.ru' />{!user && <p className='mt-1 text-sm text-gray-600'>Укажите email и подтвердите его после регистрации, чтобы позже увидеть заявку в личном кабинете.</p>}</div>
            <div className='md:col-span-2'>
              <label className='mb-2 block font-medium text-gray-700'>Опишите пожелания *</label>
              <textarea required value={formData.description} onChange={event => setFormData({ ...formData, description: event.target.value })} rows={4} className='w-full resize-none rounded-card border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary' placeholder='Куда хотите поехать, сколько человек, какие даты...' />
            </div>
          </div>
          <button type='submit' disabled={isSubmitting} className='w-full rounded-card bg-primary px-6 py-3 font-semibold text-white transition-colors hover:bg-brand-deep disabled:cursor-not-allowed disabled:opacity-60'>{isSubmitting ? 'Отправляем…' : 'Отправить заявку'}</button>
          {status && <p className='mt-3 text-center text-sm text-nature-green' role='status'>{status}</p>}
          {error && <p className='mt-3 text-center text-sm text-red-700' role='alert'>{error}</p>}
        </form>
      </div>
    </section>
  )
}

function Field({ label, value, onChange, type = 'text', required = false, placeholder }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean; placeholder: string }) {
  return <div><label className='mb-2 block font-medium text-gray-700'>{label}{required && ' *'}</label><input type={type} required={required} value={value} onChange={event => onChange(event.target.value)} className='w-full rounded-card border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary' placeholder={placeholder} /></div>
}
