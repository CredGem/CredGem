import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ActiveWalletsChart } from './active-wallets-chart';
import { AverageTransactionsPerWalletChart } from './average-transactions-per-wallet-chart';
import { MostActiveWallets } from './most-active-wallets';

export type TimeWindow = 'day' | 'week' | 'month';

// Dummy data generator
const generateDummyData = (timeWindow: TimeWindow) => {
  const points = timeWindow === 'day' ? 24 : timeWindow === 'week' ? 7 : 30;
  return Array.from({ length: points }, (_, i) => ({
    time: timeWindow === 'day' ? `${i}:00` : 
          timeWindow === 'week' ? `Day ${i + 1}` : 
          `Day ${i + 1}`,
    value: Math.floor(Math.random() * 1000)
  }));
};

const generateAverageTransactionsPerWalletData = () => {
  return {wallets: "wallets", transactions: Math.floor(Math.random() * 1000), fill: "var(--color-safari)"}
};

const generateMostActiveWalletsData = () => {
  return [
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
    { wallet: uuidv4(), transactions: Math.floor(Math.random() * 1000) },
  ]
};

const AnalyticsCard = ({ title, data }: {
  title: string;
  data: Array<{ time: string; value: number }>;
}) => (
  <Card>
    <CardHeader className="p-4 pb-0">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
    </CardHeader>
    <CardContent className="p-4">
      <div className="h-[150px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </CardContent>
  </Card>
);

export default function WalletsAnalytics() {
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('day');

  const activeWalletsData = generateDummyData(timeWindow);
  const avgTransactionsData = generateAverageTransactionsPerWalletData();
  const mostActiveWalletsData = generateMostActiveWalletsData();

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-end">
        <Select
          value={timeWindow}
          onValueChange={(value: TimeWindow) => setTimeWindow(value)}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Select time window" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="day">Daily</SelectItem>
            <SelectItem value="week">Weekly</SelectItem>
            <SelectItem value="month">Monthly</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ActiveWalletsChart
          title="Active Wallets"
          description={`Showing total active wallets for the last ${timeWindow === 'day' ? '24' : timeWindow === 'week' ? '7' : '30'} days`}
          data={activeWalletsData}
        />
        <AverageTransactionsPerWalletChart
          title="Average Transactions per Wallet"
          description={`Showing average transactions per wallet for the last ${timeWindow === 'day' ? '24' : timeWindow === 'week' ? '7' : '30'} days`}
          data={avgTransactionsData}
        />
        <MostActiveWallets  
          title="Most Active Wallets"
          description={`Showing the top 5 most active wallets for the last ${timeWindow === 'day' ? '24' : timeWindow === 'week' ? '7' : '30'} days`}
          data={mostActiveWalletsData}
        />
      </div>
    </div>
  );
}
function uuidv4() {
    return crypto.randomUUID();
}

