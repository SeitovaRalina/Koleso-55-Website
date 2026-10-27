import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { newsApi } from '../api/news'

export default function News() {
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const { data: categories } = useQuery({ queryKey: ['news-categories'], queryFn: newsApi.getCategories })
  const { data, isPending, isError, refetch } = useQuery({
    queryKey: ['news', page, category],
    queryFn: () => newsApi.getNews(page, category || undefined),
  })

  return <section className='min-h-screen bg-gray-50 py-8'>
    <div className='mx-auto max-w-7xl px-4'>
      <h1 className='mb-8 text-3xl font-bold text-gray-900'>Новости и события</h1>
      <nav aria-label='Категории новостей' className='mb-6 flex flex-wrap gap-2'>
        <button type='button' aria-pressed={!category} onClick={() => { setCategory(''); setPage(1) }} className='rounded border px-3 py-2 aria-pressed:bg-blue-100'>Все</button>
        {categories?.map(item => <button key={item.slug} type='button' aria-pressed={category === item.slug} onClick={() => { setCategory(item.slug); setPage(1) }} className='rounded border px-3 py-2 aria-pressed:bg-blue-100'>{item.name}</button>)}
      </nav>
      {isPending && <p role='status'>Загружаем новости…</p>}
      {isError && <div role='alert'>Не удалось загрузить новости. <button type='button' onClick={() => refetch()} className='font-medium text-blue-700 underline'>Повторить</button></div>}
      {data?.results.length === 0 && <p>В этой категории пока нет опубликованных новостей.</p>}
      {data && <>
        <div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>
          {data.results.map(item => <article key={item.slug} className='overflow-hidden rounded-lg bg-white shadow-md'>
            {item.cover && <Link to={`/news/${item.slug}`}><img src={item.cover} alt='' className='aspect-video w-full object-cover' /></Link>}
            <div className='p-6'>
              {item.category && <span className='rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800'>{item.category.name}</span>}
              <h2 className='mt-3 text-xl font-semibold'><Link to={`/news/${item.slug}`}>{item.title}</Link></h2>
              <time dateTime={item.published_at} className='mt-2 block text-sm text-gray-500'>{new Date(item.published_at).toLocaleDateString('ru-RU')}</time>
              <p className='mt-2 text-gray-600'>{item.excerpt}</p>
              <Link to={`/news/${item.slug}`} className='mt-4 inline-block font-medium text-blue-700 hover:underline'>Читать далее</Link>
            </div>
          </article>)}
        </div>
        {(data.previous || data.next) && <nav aria-label='Страницы новостей' className='mt-8 flex items-center justify-center gap-4'>
          <button type='button' disabled={!data.previous} onClick={() => setPage(page - 1)} className='rounded border px-4 py-2 disabled:opacity-40'>Назад</button>
          <span>Страница {page}</span>
          <button type='button' disabled={!data.next} onClick={() => setPage(page + 1)} className='rounded border px-4 py-2 disabled:opacity-40'>Далее</button>
        </nav>}
      </>}
    </div>
  </section>
}
