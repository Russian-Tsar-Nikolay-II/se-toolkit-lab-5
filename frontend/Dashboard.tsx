import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip)

export default function Dashboard(): JSX.Element {
  const data = {
    labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
    datasets: [
      {
        label: 'Scores',
        data: [5, 10, 15, 10, 5],
        backgroundColor: '#3b82f6'
      }
    ]
  }

  return <Bar data={data} />
}
EOF