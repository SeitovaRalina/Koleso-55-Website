import type { ReactNode } from 'react'
import { cn } from './utils'

interface TabItem {
  id: string
  label: string
  content: ReactNode
}

interface TabsProps {
  tabs: TabItem[]
  activeTab: string
  onChange: (tabId: string) => void
}

export function Tabs({ tabs, activeTab, onChange }: TabsProps) {
  const activeContent = tabs.find(tab => tab.id === activeTab)?.content

  return (
    <div>
      <div className='flex flex-wrap gap-2 border-b border-neutral-line'>
        {tabs.map(tab => (
          <button
            key={tab.id}
            type='button'
            onClick={() => onChange(tab.id)}
            className={cn(
              'min-h-11 rounded-t-card px-4 text-sm font-semibold text-neutral-text transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky',
              activeTab === tab.id && 'bg-brand-mist text-brand-deep',
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className='pt-5'>{activeContent}</div>
    </div>
  )
}
