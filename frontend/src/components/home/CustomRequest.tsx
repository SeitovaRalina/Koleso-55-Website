import { useState } from 'react';
import { CONTACTS } from '../../config/contacts';

export default function CustomRequest() {
  const [status, setStatus] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    description: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = encodeURIComponent('Экскурсия на заказ');
    const body = encodeURIComponent(`Имя: ${formData.name}\nТелефон: ${formData.phone}\nEmail: ${formData.email}\nПожелания: ${formData.description}`);
    setStatus('Открываем почтовую программу с заполненной заявкой.');
    window.location.href = `mailto:${CONTACTS.email}?subject=${subject}&body=${body}`;
  };

  return (
    <section className="py-16 px-4 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4">Не нашли то, что искали?</h2>
        <p className="text-gray-600 text-center mb-8">
          Оставьте заявку, и мы подберём для вас индивидуальную экскурсию
        </p>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-xl p-8 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Ваше имя</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Иван Иванов"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 font-medium mb-2">Телефон</label>
              <input
                type="tel"
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="+7 (999) 123-45-67"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-gray-700 font-medium mb-2">Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="example@mail.ru"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-gray-700 font-medium mb-2">Опишите ваши пожелания</label>
              <textarea
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                placeholder="Куда хотите поехать, сколько человек, какие даты..."
              />
            </div>
          </div>
          
          <button
            type="submit"
            className="w-full bg-primary hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Отправить заявку
          </button>
          {status && <p className="mt-3 text-center text-sm text-neutral-text" role="status">{status}</p>}
        </form>
      </div>
    </section>
  );
}
