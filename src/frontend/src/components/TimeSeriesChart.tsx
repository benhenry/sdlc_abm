/**
 * TimeSeriesChart component
 *
 * Interactive time-series chart using Plotly for visualizing metrics over time.
 */

// @ts-ignore - react-plotly.js types are incomplete
import Plot from 'react-plotly.js'

export interface TimeSeriesData {
  x: (number | string | Date)[]
  y: number[]
  name: string
  color?: string
  type?: 'line' | 'bar' | 'scatter'
  fillArea?: boolean
}

export interface TimeSeriesChartProps {
  data: TimeSeriesData[]
  title: string
  xAxisLabel?: string
  yAxisLabel?: string
  height?: number
  showLegend?: boolean
  stacked?: boolean
}

export default function TimeSeriesChart({
  data,
  title,
  xAxisLabel = 'Time',
  yAxisLabel = 'Value',
  height = 400,
  showLegend = true,
  stacked = false,
}: TimeSeriesChartProps) {
  // Convert our data format to Plotly format
  const plotlyData: any[] = data.map((series) => ({
    x: series.x,
    y: series.y,
    name: series.name,
    type: series.type || 'scatter',
    mode: series.type === 'line' || !series.type ? 'lines+markers' : undefined,
    marker: {
      color: series.color,
      size: 6,
    },
    line: {
      color: series.color,
      width: 2,
    },
    fill: series.fillArea ? 'tozeroy' : undefined,
    fillcolor: series.fillArea && series.color ? `${series.color}20` : undefined,
    stackgroup: stacked ? 'one' : undefined,
  }))

  const layout: any = {
    title: {
      text: title,
      font: {
        size: 16,
        family: 'system-ui, -apple-system, sans-serif',
      },
    },
    xaxis: {
      title: xAxisLabel,
      showgrid: true,
      gridcolor: '#e5e7eb',
    },
    yaxis: {
      title: yAxisLabel,
      showgrid: true,
      gridcolor: '#e5e7eb',
    },
    showlegend: showLegend,
    legend: {
      orientation: 'h',
      yanchor: 'bottom',
      y: -0.2,
      xanchor: 'center',
      x: 0.5,
    },
    hovermode: 'x unified',
    plot_bgcolor: 'white',
    paper_bgcolor: 'white',
    font: {
      family: 'system-ui, -apple-system, sans-serif',
      size: 12,
      color: '#374151',
    },
    margin: {
      l: 60,
      r: 40,
      t: 60,
      b: showLegend ? 80 : 50,
    },
  }

  const config: any = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: `sdlc-simlab-${title.toLowerCase().replace(/\s+/g, '-')}`,
      height: 600,
      width: 1000,
      scale: 2,
    },
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <Plot
        data={plotlyData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: `${height}px` }}
        useResizeHandler={true}
      />
    </div>
  )
}

/**
 * Helper function to generate week labels for time-series data
 */
export function generateWeekLabels(numWeeks: number, startWeek: number = 1): string[] {
  return Array.from({ length: numWeeks }, (_, i) => `Week ${startWeek + i}`)
}

/**
 * Helper function to generate day labels for time-series data
 */
export function generateDayLabels(numDays: number, startDay: number = 1): string[] {
  return Array.from({ length: numDays }, (_, i) => `Day ${startDay + i}`)
}
