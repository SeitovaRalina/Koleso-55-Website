import { excursionsApi } from '../api/excursions'
import type { Excursion } from '../types'

export async function hydrateExcursionsByIds(ids: number[]): Promise<Excursion[]> {
  if (!ids.length) {
    return []
  }

  const excursions = await excursionsApi.getExcursionsByIds(ids)
  const byId = new Map(excursions.map((excursion) => [excursion.id, excursion]))

  return ids
    .map((id) => byId.get(id))
    .filter((excursion): excursion is Excursion => Boolean(excursion))
}
