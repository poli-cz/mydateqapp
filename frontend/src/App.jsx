import React, { useEffect, useState } from "react";
import DateQDemo from "./DateQDemo";
import { getHealth } from "./api";

function BackendBadge() {
  const [status, setStatus] = useState("checking");
  const [version, setVersion] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const data = await getHealth();
        if (!cancelled) {
          setStatus(data.status === "ok" ? "online" : "degraded");
          setVersion(data.version || "");
        }
      } catch {
        if (!cancelled) {
          setStatus("offline");
        }
      }
    }

    check();
    const timer = setInterval(check, 10000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const label =
    status === "checking"
      ? "Backend: checking"
      : status === "online"
        ? `Backend: online${version ? ` · ${version}` : ""}`
        : status === "degraded"
          ? "Backend: degraded"
          : "Backend: offline";

  const borderColor =
    status === "online"
      ? "rgba(76,175,80,0.45)"
      : status === "offline"
        ? "rgba(255,71,87,0.45)"
        : "rgba(255,255,255,0.16)";

  const color =
    status === "online"
      ? "#4CAF50"
      : status === "offline"
        ? "#FF4757"
        : "rgba(255,255,255,0.8)";

  return (
    <div
      style={{
        position: "fixed",
        right: 16,
        bottom: 16,
        zIndex: 200,
        padding: "8px 12px",
        borderRadius: 999,
        border: `1px solid ${borderColor}`,
        background: "rgba(14,11,11,0.9)",
        backdropFilter: "blur(12px)",
        color,
        fontSize: 12,
        fontWeight: 700,
        boxShadow: "0 10px 30px rgba(0,0,0,0.25)",
      }}
    >
      {label}
    </div>
  );
}

export default function App() {
  return (
    <>
      <DateQDemo />
      <BackendBadge />
    </>
  );
}