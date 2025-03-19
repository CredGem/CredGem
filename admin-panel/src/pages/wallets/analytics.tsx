import { useState, useEffect } from 'react';
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
import { useInsightsStore } from '@/store/useInsightsStore';
import { WalletActivityPoint } from '@/api/insightsApi';

export type TimeWindow = 'day' | 'week' | 'month';

const generateAverageTransactionsPerWalletData = (points: WalletActivityPoint[]) => {
  const totalTransactions = points?.reduce((sum, point) => sum + point.total_transactions, 0) || 0;
  const totalWallets = points?.length || 0;
  const averageTransactionsPerWallet = totalWallets > 0 ? Math.ceil(totalTransactions / totalWallets) : 0;
  return {wallets: "wallets", transactions: averageTransactionsPerWallet, fill: "var(--color-safari)"}
};

const generateMostActiveWalletsData = (points: WalletActivityPoint[]) => {
  const mostActiveWallets = points?.sort((a, b) => b.total_transactions - a.total_transactions).slice(0, 5);
  return mostActiveWallets?.map((wallet) => ({
    wallet: wallet.wallet_name,
    transactions: wallet.total_transactions
  })) || [];
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
  const { walletActivity, fetchWalletActivity } = useInsightsStore();

  useEffect(() => {
    const now = new Date();
    const endDate = now.toISOString();
    let startDate = new Date(now);
    
    switch (timeWindow) {
      case 'day':
        startDate.setDate(startDate.getDate() - 1);
        break;
      case 'week':
        startDate.setDate(startDate.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(startDate.getMonth() - 1);
        break;
    }
    startDate.setHours(0, 0, 0, 0);

    fetchWalletActivity(startDate.toISOString(), endDate, timeWindow);
  }, [timeWindow, fetchWalletActivity]);

  // Transform wallet activity data for the chart
  const activeWalletsData = walletActivity?.points?.map(item => ({
    time: timeWindow === 'day' ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
         timeWindow === 'week' ? new Date(item.timestamp).toLocaleDateString([], { weekday: 'short' }) :
         new Date(item.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    value: item.total_transactions
  })) || [];

  const avgTransactionsData = generateAverageTransactionsPerWalletData(walletActivity?.points);
  const mostActiveWalletsData = generateMostActiveWalletsData(walletActivity?.points);

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

