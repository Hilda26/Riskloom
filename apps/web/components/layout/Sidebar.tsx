"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LoomMark } from "./LoomMark";

const NAV_SECTIONS: { label: string; items: { href: string; label: string; icon: string }[] }[] = [
  {
    label: "Overview",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: "\u2b21" },
      { href: "/alerts", label: "Risk Feed", icon: "\u25ce" },
      { href: "/oracle", label: "Oracle", icon: "\u25c8" },
    ],
  },
  {
    label: "Analysis",
    items: [
      { href: "/stablecoins", label: "Stablecoins", icon: "\u229b" },
    ],
  },
  {
    label: "Reports",
    items: [
      { href: "/reports", label: "Audit Trail", icon: "\u2261" },
      { href: "/settings", label: "Settings", icon: "\u2699" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="dsb">
      <div className="dsb-logo">
        <LoomMark size={16} />
        Riskloom
      </div>
      {NAV_SECTIONS.map((section) => (
        <div key={section.label}>
          <div className="dsb-s">{section.label}</div>
          {section.items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`dsb-i ${pathname === item.href ? "act" : ""}`}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </div>
      ))}
    </div>
  );
}
