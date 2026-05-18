"""
Analytics Service
Data processing and analysis utilities
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Service for processing analytics data"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_engagement_rate(
        self,
        likes: int,
        comments: int,
        shares: int,
        followers: int
    ) -> float:
        """
        Calculate engagement rate
        
        Formula: (likes + comments + shares) / followers * 100
        """
        if followers == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        rate = (total_engagement / followers) * 100
        
        return round(rate, 2)
    
    def calculate_growth_rate(
        self,
        current_value: int,
        previous_value: int
    ) -> float:
        """Calculate growth rate percentage"""
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        
        growth = ((current_value - previous_value) / previous_value) * 100
        return round(growth, 2)
    
    def detect_anomalies(
        self,
        data_points: List[float],
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Simple anomaly detection using standard deviation
        
        Args:
            data_points: List of numeric values
            threshold: Number of std deviations for anomaly
            
        Returns:
            List of anomalies with indices
        """
        if len(data_points) < 3:
            return []
        
        # Calculate mean and std
        mean = sum(data_points) / len(data_points)
        variance = sum((x - mean) ** 2 for x in data_points) / len(data_points)
        std_dev = variance ** 0.5
        
        anomalies = []
        for i, value in enumerate(data_points):
            z_score = abs((value - mean) / std_dev) if std_dev > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": round(z_score, 2),
                    "deviation": round(value - mean, 2)
                })
        
        return anomalies
    
    def calculate_moving_average(
        self,
        data_points: List[float],
        window_size: int = 7
    ) -> List[float]:
        """Calculate moving average"""
        if len(data_points) < window_size:
            return data_points
        
        moving_avg = []
        for i in range(len(data_points)):
            if i < window_size - 1:
                moving_avg.append(data_points[i])
            else:
                window = data_points[i - window_size + 1:i + 1]
                avg = sum(window) / window_size
                moving_avg.append(round(avg, 2))
        
        return moving_avg
    
    def aggregate_metrics(
        self,
        metrics_list: List[Dict[str, Any]],
        group_by: str = "date"
    ) -> Dict[str, Any]:
        """Aggregate metrics by specified field"""
        aggregated = {}
        
        for metric in metrics_list:
            key = metric.get(group_by, "unknown")
            
            if key not in aggregated:
                aggregated[key] = {
                    "count": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_impressions": 0
                }
            
            aggregated[key]["count"] += 1
            aggregated[key]["total_likes"] += metric.get("likes", 0)
            aggregated[key]["total_comments"] += metric.get("comments", 0)
            aggregated[key]["total_shares"] += metric.get("shares", 0)
            aggregated[key]["total_impressions"] += metric.get("impressions", 0)
        
        return aggregated
    
    def generate_time_series(
        self,
        start_date: datetime,
        days: int,
        base_value: float = 100.0,
        growth_rate: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Generate synthetic time series data for testing"""
        time_series = []
        current_value = base_value
        
        for day in range(days):
            date = start_date + timedelta(days=day)
            
            # Add some randomness
            import random
            variation = random.uniform(-0.1, 0.1)
            current_value = current_value * (1 + growth_rate + variation)
            
            time_series.append({
                "date": date.isoformat(),
                "value": round(current_value, 2)
            })
        
        return time_series
    
    def calculate_roi(
        self,
        revenue: float,
        cost: float
    ) -> float:
        """Calculate Return on Investment"""
        if cost == 0:
            return 0.0
        
        roi = ((revenue - cost) / cost) * 100
        return round(roi, 2)


# Global instance
analytics_processor = AnalyticsProcessor()
