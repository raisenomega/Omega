import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface PlatformData {
  platform: string;
  count: number;
  followers: number;
  connected: number;
}

const PLATFORM_LABELS: Record<string, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  twitter: "X/Twitter",
  linkedin: "LinkedIn",
  youtube: "YouTube",
};

const PLATFORM_COLORS: Record<string, string> = {
  instagram: "hsl(340, 75%, 55%)",
  facebook: "hsl(220, 70%, 50%)",
  tiktok: "hsl(0, 0%, 10%)",
  twitter: "hsl(200, 80%, 50%)",
  linkedin: "hsl(210, 70%, 45%)",
  youtube: "hsl(0, 80%, 50%)",
};

interface PlatformChartsProps {
  data: PlatformData[];
}

export function FollowersByPlatformChart({ data }: PlatformChartsProps) {
  const chartData = data
    .filter((d) => d.followers > 0)
    .map((d) => ({
      name: PLATFORM_LABELS[d.platform] || d.platform,
      followers: d.followers,
      fill: PLATFORM_COLORS[d.platform] || "hsl(var(--primary))",
    }));

  if (chartData.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg">Seguidores por Plataforma</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Agrega cuentas sociales para ver datos</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Seguidores por Plataforma</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              formatter={(value: number) => [value.toLocaleString(), "Seguidores"]}
            />
            <Bar dataKey="followers" radius={[6, 6, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function AccountDistributionChart({ data }: PlatformChartsProps) {
  const pieData = data
    .filter((d) => d.count > 0)
    .map((d) => ({
      name: PLATFORM_LABELS[d.platform] || d.platform,
      value: d.count,
      fill: PLATFORM_COLORS[d.platform] || "hsl(var(--primary))",
    }));

  if (pieData.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg">Distribución de Cuentas</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Sin cuentas registradas</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Distribución de Cuentas</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={4}
              dataKey="value"
              label={({ name, value }) => `${name}: ${value}`}
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
