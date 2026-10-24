import type { Excursion, ExcursionSlot } from '../types'

const shortDate = (value: string) => {
  const [, month, day] = value.split('-')
  return `${day}.${month}`
}

const shortTime = (value: string) => value.slice(0, 5)

export function formatSlot(slot: ExcursionSlot, compact = false) {
  const start = `${shortDate(slot.date)} ${shortTime(slot.time)}`
  if (!slot.end_date || !slot.end_time) return start
  if (compact && slot.end_date !== slot.date) {
    return `${shortDate(slot.date)} – ${shortDate(slot.end_date)}`
  }
  if (compact && slot.end_date === slot.date) {
    return `${start}–${shortTime(slot.end_time)}`
  }
  return `${start} – ${shortDate(slot.end_date)} ${shortTime(slot.end_time)}`
}

export function formatDuration(excursion: Excursion, slot?: ExcursionSlot | null) {
  if (excursion.is_multi_day) {
    if (!slot?.end_date) return 'Длительность уточняется'
    const start = Date.parse(`${slot.date}T00:00:00Z`)
    const end = Date.parse(`${slot.end_date}T00:00:00Z`)
    const days = Math.round((end - start) / 86400000) + 1
    return `${days} ${days % 10 === 1 && days % 100 !== 11 ? 'день' : days % 10 >= 2 && days % 10 <= 4 && (days % 100 < 12 || days % 100 > 14) ? 'дня' : 'дней'}`
  }
  const hours = Math.floor(excursion.duration / 60)
  const minutes = excursion.duration % 60
  return [hours && `${hours} ч`, minutes && `${minutes} мин`].filter(Boolean).join(' ') || '0 мин'
}

export function getPrice(excursion: Excursion, slot?: ExcursionSlot | null) {
  const tariffs = excursion.ticket_types?.filter(ticket => ticket.is_active) || []
  const prices = tariffs.length ? tariffs.map(ticket => Number(ticket.price)) : [Number(excursion.price)]
  const minimum = slot?.price_override != null ? Number(slot.price_override) : Math.min(...prices)
  return { amount: minimum, from: tariffs.length > 1, exact: tariffs.length <= 1 && !!slot }
}
