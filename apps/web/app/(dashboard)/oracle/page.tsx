import { OracleIntegrationList } from "@/components/oracle/OracleIntegrationList";
import { LiveContractPanel } from "@/components/oracle/LiveContractPanel";

export default function OraclePage() {
  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Risk Oracle</div>
          <div className="dm-sub">GenLayer StudioNet - StableScoreOracle</div>
        </div>
      </div>
      <div className="oracle-wrap">
        <div className="oracle-grid">
          <OracleIntegrationList />
          <LiveContractPanel />
        </div>
      </div>
    </>
  );
}
