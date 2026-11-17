// JSDoc type hints for JS usage; TS consumers get real types from registry
/**
 * @typedef {string|number|Date} ChartValue
 */
/**
 * @typedef {Record<string, ChartValue>} ChartDataRecord
 */
/**
 * @template T
 * @typedef {Object} BaseChartProps
 * @property {T[]} data
 * @property {keyof T} index
 * @property {string[]=} colors
 * @property {{ top?: number, right?: number, bottom?: number, left?: number }=} margin
 * @property {boolean=} showLegend
 * @property {boolean=} showTooltip
 * @property {number=} filterOpacity
 */

export {}
