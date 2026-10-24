import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { newsApi } from '../api/news'

export default function News() {
  const [page, setPage] = useState(1)
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null)
  const { data, isPending, isError, refetch } = useQuery({
    queryKey: ['news', page],
    queryFn: () => newsApi.getNews(page),
  })

  return <section className='min-h-screen bg-gray-50 py-8'>
    <div className='mx-auto max-w-7xl px-4'>
      <h1 className='mb-8 text-3xl font-bold text-gray-900'>Новости и события</h1>
      {isPending && <p role='status'>Загружаем новости…</p>}
      {isError && <div role='alert'>Не удалось загрузить новости. <button type='button' onClick={() => refetch()} className='font-medium text-blue-700 underline'>Повторить</button></div>}
      {data?.results.length === 0 && <p>Пока нет опубликованных новостей.</p>}
      {data && <>
        <div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>
          {data.results.map(item => <article key={item.slug} className='overflow-hidden rounded-lg bg-white shadow-md'>
            {item.cover && <img src={item.cover} alt='' className='aspect-video w-full object-cover' />}
            <div className='p-6'>
              {item.category && <span className='rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800'>{item.category}</span>}
              <h2 className='mt-3 text-xl font-semibold'>{item.title}</h2>
              <time dateTime={item.published_at} className='mt-2 block text-sm text-gray-500'>{new Date(item.published_at).toLocaleDateString('ru-RU')}</time>
              <p className='mt-2 text-gray-600'>{item.excerpt}</p>
              <button type='button' aria-expanded={expandedSlug === item.slug} onClick={() => setExpandedSlug(expandedSlug === item.slug ? null : item.slug)} className='mt-4 font-medium text-blue-600 hover:text-blue-700'>
                {expandedSlug === item.slug ? 'Свернуть' : 'Читать далее'}
              </button>
              {expandedSlug === item.slug && <div className='mt-4 whitespace-pre-wrap border-t pt-4 text-gray-700'>{item.body}</div>}
            </div>
          </article>)}
        </div>
        {(data.previous || data.next) && <nav aria-label='Страницы новостей' className='mt-8 flex items-center justify-center gap-4'>
          <button type='button' disabled={!data.previous} onClick={() => { setExpandedSlug(null); setPage(page - 1) }} className='rounded border px-4 py-2 disabled:opacity-40'>Назад</button>
          <span>Страница {page}</span>
          <button type='button' disabled={!data.next} onClick={() => { setExpandedSlug(null); setPage(page + 1) }} className='rounded border px-4 py-2 disabled:opacity-40'>Далее</button>
        </nav>}
      </>}
    </div>
  </section>
}
