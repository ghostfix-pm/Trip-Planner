import logging
import random
import numpy as np
from sklearn.cluster import KMeans
from app.agents.state import AgentState

logger = logging.getLogger("trip_planner")

async def cluster_agent_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    duration_days = int(user_intent.get("duration_days", 1))
    travel_pace = user_intent.get("travel_pace", "balanced").lower()
    activity_candidates = state.get("activity_candidates", [])

    valid_acts = [a for a in activity_candidates if a.get("latitude") and a.get("longitude")]
    
    if not valid_acts:
        logger.warning("⚠️ [Cluster Agent] Không có địa danh hợp lệ để phân cụm.")
        return {"activity_clusters": []}

    if travel_pace == "relaxed":
        min_per_day, max_per_day = 2, 3
    elif travel_pace == "packed":
        min_per_day, max_per_day = 5, 6
    else:
        min_per_day, max_per_day = 3, 4

    target_total = random.randint(min_per_day * duration_days, max_per_day * duration_days)
    selected_acts = valid_acts[:target_total]

    num_clusters = min(duration_days, len(selected_acts))
    
    coords = np.array([[a["latitude"], a["longitude"]] for a in selected_acts])
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)
    centers = kmeans.cluster_centers_

    clusters = []
    for i in range(num_clusters):
        cluster_acts = [selected_acts[j] for j in range(len(selected_acts)) if labels[j] == i]
        
        clusters.append({
            "cluster_id": i + 1,
            "center_lat": centers[i][0],
            "center_lng": centers[i][1],
            "activities": cluster_acts,
            "foods": []
        })

    return {
        "activity_clusters": clusters,
        "messages": [f"[Cluster Agent]: Đã chọn top {len(selected_acts)}/{len(valid_acts)} địa điểm và gom thành {num_clusters} cụm."]
    }