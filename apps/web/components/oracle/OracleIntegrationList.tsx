const INTEGRATIONS = [
  {
    icon: "\ud83c\udfe6",
    iconClass: "oi-v",
    name: "Lending Protocols",
    desc: "Auto-reduce borrow limits when rating drops below BBB",
    status: "Live",
  },
  {
    icon: "\ud83c\udfdb",
    iconClass: "oi-a",
    name: "Treasury Systems",
    desc: "Rebalance reserves when any holding drops below A",
    status: "Live",
  },
  {
    icon: "\ud83d\udcb3",
    iconClass: "oi-s",
    name: "Payment Networks",
    desc: "Accept only stablecoins rated BBB or above",
    status: "Ready",
  },
  {
    icon: "\u26a1",
    iconClass: "oi-v",
    name: "Liquidation Engines",
    desc: "Trigger early liquidation on CCC-rated collateral",
    status: "Ready",
  },
];

export function OracleIntegrationList() {
  return (
    <div className="oracle-left">
      <div className="oracle-lbl">Oracle Integrations</div>
      {INTEGRATIONS.map((item) => (
        <div className="oracle-item" key={item.name}>
          <div className={`oi-icon ${item.iconClass}`}>{item.icon}</div>
          <div>
            <div className="oi-name">{item.name}</div>
            <div className="oi-desc">{item.desc}</div>
          </div>
          <div className={`oi-status ${item.status === "Live" ? "ois-live" : "ois-ready"}`}>
            {item.status}
          </div>
        </div>
      ))}
    </div>
  );
}
