import { useQuery } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import { Link, useParams } from 'react-router-dom'
import { newsApi } from '../api/news'

export default function NewsDetail() {
  const { slug = '' } = useParams()
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['news-article', slug],
    queryFn: () => newsApi.getArticle(slug),
    enabled: Boolean(slug),
  })

  return <main className='min-h-screen bg-gray-50 py-8'>
    <article className='mx-auto max-w-3xl px-4'>
      <Link to='/news' className='text-blue-700 hover:underline'>← Все новости</Link>
      {isPending && <p role='status' className='mt-8'>Загружаем материал…</p>}
      {error && <div role='alert' className='mt-8'>
        {isAxiosError(error) && error.response?.status === 404 ? 'Новость не найдена.' : <>Не удалось загрузить материал. <button type='button' onClick={() => refetch()} className='text-blue-700 underline'>Повторить</button></>}
      </div>}
      {data && <>
        <header className='mt-8'>
          {data.category && <span className='text-sm font-medium text-blue-700'>{data.category.name}</span>}
          <h1 className='mt-2 text-3xl font-bold text-gray-900 md:text-5xl'>{data.title}</h1>
          <time dateTime={data.published_at} className='mt-4 block text-sm text-gray-500'>{new Date(data.published_at).toLocaleDateString('ru-RU')}</time>
          <p className='mt-6 text-lg text-gray-700'>{data.excerpt}</p>
        </header>
        {data.cover && <img src={data.cover} alt='' className='mt-8 w-full rounded-lg object-cover' />}
        <div className='mt-10 space-y-6 text-gray-800'>
          {data.blocks.map((block, index) => {
            if (block.kind === 'heading') return <h2 key={index} className='text-2xl font-semibold'>{block.text}</h2>
            if (block.kind === 'paragraph') return <p key={index} className='whitespace-pre-wrap leading-7'>{block.text}</p>
            return <figure key={index}><img src={block.image || ''} alt={block.alt} className='w-full rounded-lg object-cover' />{block.caption && <figcaption className='mt-2 text-sm text-gray-600'>{block.caption}</figcaption>}</figure>
          })}
        </div>
      </>}
    </article>
  </main>
}
