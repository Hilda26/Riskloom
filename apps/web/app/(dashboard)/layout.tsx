import { Sidebar } from "@/components/layout/Sidebar";
import { WalletGuard } from "@/components/wallet/WalletGuard";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ paddingTop: "62px", position: "relative", zIndex: 2, minHeight: "100vh" }}>
      <WalletGuard>
        <div className="dash-grid" style={{ minHeight: "calc(100vh - 62px)" }}>
          <Sidebar />
          <div className="dm">{children}</div>
        </div>
      </WalletGuard>
    </div>
  );
}
