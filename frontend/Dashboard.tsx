cat > src/Dashboard.tsx << 'EOF'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  ChartOptions
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip)

interface ScoreChartData {
  labels: string[]
  datasets: Array<{
    label: string
     number[]
    backgroundColor: string
  }>
}

export default function Dashboard(): JSX.Element {
  const chartData: ScoreChartData = {
    labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
    datasets: [{
      label: 'Scores',
       [5, 10, 15, 10, 5],
      backgroundColor: '#3b82f6'
    }]
  }

  const chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Score Distribution' }
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <Bar data={chartData} options={chartOptions} />
    </div>
  )
}
EOF