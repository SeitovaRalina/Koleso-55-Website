import { useState } from 'react'

const articles = [
  { id: 1, title: 'Топ-5 экскурсий на выходные', excerpt: 'Лучшие направления для коротких путешествий.', category: 'Советы' },
  { id: 2, title: 'Новые маршруты по Алтаю', excerpt: 'Природные достопримечательности и новые даты.', category: 'Новости' },
  { id: 3, title: 'Как подготовиться к зимней экскурсии', excerpt: 'Что взять с собой для комфортной поездки.', category: 'Советы' },
]

export default function News() {
  const [expandedId, setExpandedId] = useState<number | null>(null)
  return <section className='min-h-screen bg-gray-50 py-8'><div className='mx-auto max-w-7xl px-4'><h1 className='mb-8 text-3xl font-bold text-gray-900'>Новости и события</h1><div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>{articles.map(article => <article key={article.id} className='overflow-hidden rounded-lg bg-white shadow-md'><div className='h-40 bg-brand-mist' /><div className='p-6'><span className='rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800'>{article.category}</span><h2 className='mt-3 text-xl font-semibold'>{article.title}</h2><p className='mt-2 text-gray-600'>{article.excerpt}</p><button type='button' onClick={() => setExpandedId(expandedId === article.id ? null : article.id)} className='mt-4 font-medium text-blue-600 hover:text-blue-700'>{expandedId === article.id ? 'Свернуть' : 'Читать далее'}</button>{expandedId === article.id && <p className='mt-4 border-t pt-4 text-gray-700'>Материал будет дополнен редакцией. Следите за афишей, чтобы не пропустить новые экскурсии.</p>}</div></article>)}</div></div></section>
}
