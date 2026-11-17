// Re-export runtime chart utilities and components from the app's chart module
export {
  ChartCrosshair,
  ChartLegend,
  ChartSingleTooltip,
  ChartTooltip,
  defaultColors,
} from '@/components/ui/chart'

// Type definitions expected by shadcn-vue charts
export type ChartValue = string | number | Date

export type ChartDataRecord = Record<string, ChartValue>

export interface BaseChartProps<T extends ChartDataRecord = ChartDataRecord> {
  data: T[]
  index: keyof T
  colors?: string[]
  margin?: { top?: number; right?: number; bottom?: number; left?: number }
  showLegend?: boolean
  showTooltip?: boolean
  filterOpacity?: number
}
