import React from 'react';
import { Badge, Tooltip } from 'antd';

export const SiteStatusBadge = ({ status, latencyMs, name, size = 'default' }) => {
  const isOnline = status === 'ONLINE' || status === 'HEALTHY';
  const badgeStatus = isOnline ? 'success' : 'error';
  const textStatus = isOnline ? 'Online' : 'Offline';

  return (
    <Tooltip
      title={
        <div>
          <div><strong>{name}</strong></div>
          <div>Trạng thái: {textStatus}</div>
          {latencyMs !== undefined && <div>Độ trễ: {latencyMs} ms</div>}
        </div>
      }
    >
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-white shadow-sm cursor-pointer">
        <Badge status={badgeStatus} />
        <span className="font-semibold text-slate-700">{name || 'Node'}</span>
        {latencyMs !== undefined && (
          <span className={`text-[11px] ${latencyMs > 50 ? 'text-amber-500' : 'text-slate-400'}`}>
            ({latencyMs}ms)
          </span>
        )}
      </span>
    </Tooltip>
  );
};

export default SiteStatusBadge;
