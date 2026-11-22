from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.schemas.system import NodeHealthStatus, SystemHealthData, AuditLogPagination, AuditLogItem
import app.repositories.health_repo as health_repo


def get_system_health() -> SystemHealthData:
    """
    Kiểm tra sức khỏe 3 node CSDL PostgreSQL và MinIO Object Storage:
    - Đo độ trễ (latency ms).
    - Xử lý Graceful Degradation: Nếu 1 node offline, đánh dấu OFFLINE mà không làm sập backend.
    """
    nodes: List[NodeHealthStatus] = []
    overall_status = "HEALTHY"

    # 1. Node site_hn (Coordinator & Shard HN)
    hn_online, hn_latency, hn_err = health_repo.check_node_latency("site_hn")
    if not hn_online:
        overall_status = "DEGRADED"
    nodes.append(NodeHealthStatus(
        node_id="site_hn",
        name="Hà Nội Coordinator",
        role="Coordinator & Shard",
        host=f"{settings.DB_HN_HOST}:{settings.DB_HN_PORT}",
        status="ONLINE" if hn_online else "OFFLINE",
        latency_ms=hn_latency,
        database=settings.DB_HN_NAME,
        error=hn_err
    ))

    # 2. Node site_dn (Shard DN)
    dn_online, dn_latency, dn_err = health_repo.check_node_latency("site_dn")
    if not dn_online:
        overall_status = "DEGRADED"
    nodes.append(NodeHealthStatus(
        node_id="site_dn",
        name="Đà Nẵng Shard",
        role="Horizontal Shard",
        host=f"{settings.DB_DN_HOST}:{settings.DB_DN_PORT}",
        status="ONLINE" if dn_online else "OFFLINE",
        latency_ms=dn_latency,
        database=settings.DB_DN_NAME,
        error=dn_err
    ))

    # 3. Node site_hcm (Shard HCM)
    hcm_online, hcm_latency, hcm_err = health_repo.check_node_latency("site_hcm")
    if not hcm_online:
        overall_status = "DEGRADED"
    nodes.append(NodeHealthStatus(
        node_id="site_hcm",
        name="TP.HCM Shard",
        role="Horizontal Shard",
        host=f"{settings.DB_HCM_HOST}:{settings.DB_HCM_PORT}",
        status="ONLINE" if hcm_online else "OFFLINE",
        latency_ms=hcm_latency,
        database=settings.DB_HCM_NAME,
        error=hcm_err
    ))

    # 4. MinIO Object Storage
    minio_online, minio_latency, minio_err = health_repo.check_minio_health()
    if not minio_online:
        overall_status = "DEGRADED"
    nodes.append(NodeHealthStatus(
        node_id="minio_server",
        name="MinIO S3 Storage",
        role="Object Storage",
        host=settings.MINIO_ENDPOINT,
        status="ONLINE" if minio_online else "OFFLINE",
        latency_ms=minio_latency,
        bucket=settings.MINIO_BUCKET,
        error=minio_err
    ))

    return SystemHealthData(
        overall_status=overall_status,
        nodes=nodes
    )


def get_audit_trail(
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> AuditLogPagination:
    """Tra cứu nhật ký kiểm toán hệ thống."""
    raw_logs, total = health_repo.get_audit_logs(
        keyword=keyword,
        page=page,
        page_size=page_size
    )

    items = [
        AuditLogItem(
            id=l["id"],
            thoi_gian=l["thoigian"],
            ma_nv_thuc_hien=l.get("manvthuchien"),
            ten_nv_thuc_hien=l.get("tennvthuchien"),
            thao_tac=l.get("thaotac", ""),
            tac_dong_len_nv=l.get("tacdonglennv"),
            chi_tiet=l.get("chitiet")
        )
        for l in raw_logs
    ]

    return AuditLogPagination(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
