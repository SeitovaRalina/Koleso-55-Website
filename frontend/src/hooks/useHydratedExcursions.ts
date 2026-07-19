import { useQuery } from '@tanstack/react-query'
import { hydrateExcursionsByIds } from '../utils/hydrateExcursions'

export function useHydratedExcursions(ids: number[]) {
  return useQuery({
    queryKey: ['excursions-by-ids', ids],
    queryFn: () => hydrateExcursionsByIds(ids),
    enabled: ids.length > 0,
  })
}
