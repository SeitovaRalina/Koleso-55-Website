export default function News() {
  const articles = [
    {
      id: 1,
      title: 'Топ-5 экскурсий на выходные',
      excerpt: 'Откройте для себя лучшие направления для коротких путешествий',
      image: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800',
      date: '2024-01-15',
      category: 'Советы',
    },
    {
      id: 2,
      title: 'Новые маршруты по Алтаю',
      excerpt: 'Уникальные природные достопримечательности ждут вас',
      image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
      date: '2024-01-10',
      category: 'Новости',
    },
    {
      id: 3,
      title: 'Как подготовиться к зимней экскурсии',
      excerpt: 'Полное руководство для комфортного путешествия',
      image: 'https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?w=800',
      date: '2024-01-05',
      category: 'Советы',
    },
    {
      id: 4,
      title: 'Скидки для постоянных клиентов',
      excerpt: 'Узнайте о нашей программе лояльности',
      image: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800',
      date: '2024-01-01',
      category: 'Акции',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Новости и события</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {articles.map((article) => (
            <article key={article.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              {article.image && (
                <img
                  src={article.image}
                  alt={article.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                    {article.category}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(article.date).toLocaleDateString('ru-RU')}
                  </span>
                </div>
                <h2 className="text-xl font-semibold mb-2">{article.title}</h2>
                <p className="text-gray-600 mb-4">{article.excerpt}</p>
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  Читать далее →
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  )
}
