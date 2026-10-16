"""Bounded closed-schema operational indicators. No logs, secrets or IO."""
def observe(*, queue_depth, queue_bytes, disk_free_bytes, rss_bytes,
            retries, sources, max_queue_depth=100, max_queue_bytes=1048576,
            min_disk_free_bytes=1073741824, max_rss_bytes=268435456,
            max_retries=3):
    values=[queue_depth,queue_bytes,disk_free_bytes,rss_bytes,retries]
    limits=[max_queue_depth,max_queue_bytes,min_disk_free_bytes,max_rss_bytes,max_retries]
    if any(type(x) is not int or x<0 for x in values) or any(type(x) is not int or x<1 for x in limits):
        raise ValueError("invalid counters or limits")
    if not isinstance(sources,list) or len(sources)>1000 or any(
        x not in {"SUCCESS","DEGRADED","UNAVAILABLE","UNKNOWN"} for x in sources):
        raise ValueError("invalid source states")
    reasons=[]
    for exceeds,label in [
        (queue_depth>max_queue_depth,"QUEUE_DEPTH"),
        (queue_bytes>max_queue_bytes,"QUEUE_BYTES"),
        (disk_free_bytes<min_disk_free_bytes,"DISK_LOW"),
        (rss_bytes>max_rss_bytes,"MEMORY"),
        (retries>=max_retries,"RETRY_EXHAUSTED")]:
        if exceeds: reasons.append(label)
    counts={s:sources.count(s) for s in ["SUCCESS","DEGRADED","UNAVAILABLE","UNKNOWN"]}
    blocked=bool(reasons)
    if not sources or counts["UNKNOWN"]: reasons.append("SOURCE_UNKNOWN")
    if counts["DEGRADED"] or counts["UNAVAILABLE"]: reasons.append("SOURCE_DEGRADED")
    return {"version":1,"status":"BLOCKED" if blocked else "DEGRADED" if reasons else "HEALTHY",
            "admit_work":not reasons,"reasons":reasons,"source_counts":counts,
            "counters":dict(zip(["queue_depth","queue_bytes","disk_free_bytes","rss_bytes","retries"],values)),
            "send":False}
