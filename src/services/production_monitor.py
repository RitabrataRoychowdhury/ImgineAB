"""
Production Monitoring and Health Check System for Enhanced Contract Assistant

This module provides comprehensive monitoring, health checks, performance tracking,
error handling, and production readiness validation.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import json
import asyncio
import threading
import psutil
import logging
from collections import deque, defaultdict
import statistics

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


class MetricType(Enum):
    """Types of metrics to track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheck:
    """Individual health check definition"""
    name: str
    check_function: Callable[[], bool]
    critical: bool = False
    timeout_seconds: int = 5
    description: str = ""


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Individual metric value"""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    response_times: List[float]
    throughput: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_sessions: int
    cache_hit_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    metric_name: str
    threshold: float
    comparison: str  # gt, lt, eq, gte, lte
    duration_minutes: int = 5
    severity: str = "warning"  # info, warning, critical
    description: str = ""


@dataclass
class Alert:
    """Active alert"""
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class ProductionMonitor:
    """
    Production monitoring system that provides:
    - Comprehensive health checks for all system components
    - Real-time performance metrics collection and analysis
    - Automated alerting for critical issues
    - System resource monitoring and optimization
    - Error tracking and analysis
    - Production readiness validation
    """
    
    def __init__(self, 
                 metrics_retention_hours: int = 24,
                 health_check_interval_seconds: int = 30,
                 alert_check_interval_seconds: int = 60):
        """Initialize the production monitor"""
        
        self.metrics_retention_hours = metrics_retention_hours
        self.health_check_interval = health_check_interval_seconds
        self.alert_check_interval = alert_check_interval_seconds
        
        # Metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_history: deque = deque(maxlen=1000)
        
        # Health checks
        self.health_checks: List[HealthCheck] = []
        self.last_health_results: Dict[str, HealthCheckResult] = {}
        
        # Alerting
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize default health checks and alert rules
        self._initialize_default_health_checks()
        self._initialize_default_alert_rules()
        
    def start_monitoring(self) -> None:
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Production monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Production monitoring stopped")
    
    def record_metric(self, 
                     name: str, 
                     value: float, 
                     metric_type: MetricType = MetricType.GAUGE,
                     tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""
        
        metric_value = MetricValue(
            value=value,
            tags=tags or {}
        )
        
        self.metrics[name].append(metric_value)
        
        # Clean up old metrics
        self._cleanup_old_metrics()
    
    def record_response_time(self, response_time: float, endpoint: str = "default") -> None:
        """Record response time metric"""
        self.record_metric(
            f"response_time_{endpoint}",
            response_time,
            MetricType.TIMER,
            {"endpoint": endpoint}
        )
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> None:
        """Record error occurrence"""
        self.record_metric(
            f"error_{error_type}",
            1,
            MetricType.COUNTER,
            {"error_type": error_type, "message": error_message[:100]}
        )
        
        # Log error details
        logger.error(f"Error recorded: {error_type} - {error_message}", extra=context or {})
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        
        # Run health checks if not recently executed
        current_time = datetime.now()
        if (not self.last_health_results or 
            any((current_time - result.timestamp).seconds > self.health_check_interval 
                for result in self.last_health_results.values())):
            self._run_health_checks()
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        critical_issues = []
        warnings = []
        
        for result in self.last_health_results.values():
            if result.status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                critical_issues.append(result.name)
            elif result.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.WARNING
                warnings.append(result.name)
        
        return {
            "overall_status": overall_status.value,
            "timestamp": current_time.isoformat(),
            "checks": {
                result.name: {
                    "status": result.status.value,
                    "message": result.message,
                    "execution_time": result.execution_time,
                    "details": result.details
                }
                for result in self.last_health_results.values()
            },
            "critical_issues": critical_issues,
            "warnings": warnings,
            "active_alerts": len(self.active_alerts)
        }
    
    def get_performance_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance metrics for specified time window"""
        
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Filter recent metrics
        recent_metrics = {}
        for metric_name, values in self.metrics.items():
            recent_values = [
                v.value for v in values 
                if v.timestamp >= cutoff_time
            ]
            if recent_values:
                recent_metrics[metric_name] = {
                    "count": len(recent_values),
                    "avg": statistics.mean(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "p95": statistics.quantiles(recent_values, n=20)[18] if len(recent_values) > 20 else max(recent_values)
                }
        
        # System metrics
        system_metrics = self._get_system_metrics()
        
        # Calculate derived metrics
        response_time_metrics = [m for name, m in recent_metrics.items() if "response_time" in name]
        error_metrics = [m for name, m in recent_metrics.items() if "error" in name]
        
        avg_response_time = statistics.mean([m["avg"] for m in response_time_metrics]) if response_time_metrics else 0.0
        total_errors = sum(m["count"] for m in error_metrics)
        total_requests = sum(m["count"] for name, m in recent_metrics.items() if "request" in name)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "time_window_minutes": time_window_minutes,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "avg_response_time": avg_response_time,
                "error_rate_percent": error_rate,
                "total_requests": total_requests,
                "total_errors": total_errors
            },
            "system": system_metrics,
            "metrics": recent_metrics
        }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        return [
            {
                "rule_name": alert.rule_name,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold": alert.threshold,
                "severity": alert.severity,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
                "duration_minutes": (datetime.now() - alert.triggered_at).total_seconds() / 60
            }
            for alert in self.active_alerts.values()
        ]
    
    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add a custom health check"""
        self.health_checks.append(health_check)
        logger.info(f"Added health check: {health_check.name}")
    
    def add_alert_rule(self, alert_rule: AlertRule) -> None:
        """Add a custom alert rule"""
        self.alert_rules.append(alert_rule)
        logger.info(f"Added alert rule: {alert_rule.name}")
    
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate system readiness for production deployment"""
        
        readiness_checks = {
            "health_checks_passing": self._check_health_status(),
            "performance_acceptable": self._check_performance_thresholds(),
            "error_rates_low": self._check_error_rates(),
            "resource_usage_normal": self._check_resource_usage(),
            "dependencies_available": self._check_dependencies(),
            "configuration_valid": self._check_configuration(),
            "monitoring_active": self.monitoring_active,
            "alerts_configured": len(self.alert_rules) > 0
        }
        
        all_checks_pass = all(readiness_checks.values())
        
        return {
            "production_ready": all_checks_pass,
            "timestamp": datetime.now().isoformat(),
            "checks": readiness_checks,
            "recommendations": self._get_production_recommendations(readiness_checks)
        }
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        last_health_check = datetime.now() - timedelta(seconds=self.health_check_interval)
        last_alert_check = datetime.now() - timedelta(seconds=self.alert_check_interval)
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Run health checks
                if (current_time - last_health_check).seconds >= self.health_check_interval:
                    self._run_health_checks()
                    last_health_check = current_time
                
                # Check alerts
                if (current_time - last_alert_check).seconds >= self.alert_check_interval:
                    self._check_alerts()
                    last_alert_check = current_time
                
                # Record system metrics
                self._record_system_metrics()
                
                # Sleep for a short interval
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _run_health_checks(self) -> None:
        """Run all configured health checks"""
        
        for health_check in self.health_checks:
            try:
                start_time = time.time()
                
                # Run check with timeout
                result = self._run_single_health_check(health_check)
                execution_time = time.time() - start_time
                
                # Create result
                if result:
                    status = HealthStatus.HEALTHY
                    message = "Check passed"
                else:
                    status = HealthStatus.CRITICAL if health_check.critical else HealthStatus.WARNING
                    message = "Check failed"
                
                health_result = HealthCheckResult(
                    name=health_check.name,
                    status=status,
                    message=message,
                    execution_time=execution_time
                )
                
                self.last_health_results[health_check.name] = health_result
                
            except Exception as e:
                logger.error(f"Health check {health_check.name} failed with exception: {e}")
                
                self.last_health_results[health_check.name] = HealthCheckResult(
                    name=health_check.name,
                    status=HealthStatus.CRITICAL,
                    message=f"Exception: {str(e)}",
                    execution_time=0.0
                )
    
    def _run_single_health_check(self, health_check: HealthCheck) -> bool:
        """Run a single health check with timeout"""
        try:
            # Simple timeout implementation
            return health_check.check_function()
        except Exception as e:
            logger.error(f"Health check {health_check.name} exception: {e}")
            return False
    
    def _check_alerts(self) -> None:
        """Check alert rules and trigger/resolve alerts"""
        
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            try:
                # Get recent metric values
                metric_values = self._get_recent_metric_values(
                    rule.metric_name, 
                    rule.duration_minutes
                )
                
                if not metric_values:
                    continue
                
                # Calculate current value (average over duration)
                current_value = statistics.mean(metric_values)
                
                # Check threshold
                threshold_breached = self._check_threshold(
                    current_value, 
                    rule.threshold, 
                    rule.comparison
                )
                
                alert_key = f"{rule.name}_{rule.metric_name}"
                
                if threshold_breached:
                    # Trigger alert if not already active
                    if alert_key not in self.active_alerts:
                        alert = Alert(
                            rule_name=rule.name,
                            metric_name=rule.metric_name,
                            current_value=current_value,
                            threshold=rule.threshold,
                            severity=rule.severity,
                            message=f"{rule.description}: {current_value} {rule.comparison} {rule.threshold}"
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        
                        logger.warning(f"Alert triggered: {alert.message}")
                
                else:
                    # Resolve alert if active
                    if alert_key in self.active_alerts:
                        alert = self.active_alerts[alert_key]
                        alert.resolved_at = current_time
                        
                        del self.active_alerts[alert_key]
                        
                        logger.info(f"Alert resolved: {alert.rule_name}")
                        
            except Exception as e:
                logger.error(f"Error checking alert rule {rule.name}: {e}")
    
    def _record_system_metrics(self) -> None:
        """Record system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system_cpu_percent", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric("system_memory_percent", memory.percent)
            self.record_metric("system_memory_mb", memory.used / 1024 / 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.record_metric("system_disk_percent", disk.percent)
            
            # Network I/O (if available)
            try:
                network = psutil.net_io_counters()
                self.record_metric("system_network_bytes_sent", network.bytes_sent)
                self.record_metric("system_network_bytes_recv", network.bytes_recv)
            except:
                pass  # Network stats might not be available
                
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _get_recent_metric_values(self, metric_name: str, duration_minutes: int) -> List[float]:
        """Get recent metric values within time window"""
        if metric_name not in self.metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        return [
            value.value for value in self.metrics[metric_name]
            if value.timestamp >= cutoff_time
        ]
    
    def _check_threshold(self, current_value: float, threshold: float, comparison: str) -> bool:
        """Check if current value breaches threshold"""
        if comparison == "gt":
            return current_value > threshold
        elif comparison == "lt":
            return current_value < threshold
        elif comparison == "gte":
            return current_value >= threshold
        elif comparison == "lte":
            return current_value <= threshold
        elif comparison == "eq":
            return current_value == threshold
        else:
            logger.warning(f"Unknown comparison operator: {comparison}")
            return False
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up old metric values"""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        
        for metric_name in list(self.metrics.keys()):
            values = self.metrics[metric_name]
            
            # Remove old values
            while values and values[0].timestamp < cutoff_time:
                values.popleft()
            
            # Remove empty metrics
            if not values:
                del self.metrics[metric_name]
    
    def _initialize_default_health_checks(self) -> None:
        """Initialize default health checks"""
        
        # System health checks
        self.health_checks.extend([
            HealthCheck(
                name="system_memory",
                check_function=lambda: psutil.virtual_memory().percent < 90,
                critical=True,
                description="Check system memory usage"
            ),
            HealthCheck(
                name="system_cpu",
                check_function=lambda: psutil.cpu_percent(interval=1) < 95,
                critical=True,
                description="Check system CPU usage"
            ),
            HealthCheck(
                name="system_disk",
                check_function=lambda: psutil.disk_usage('/').percent < 95,
                critical=True,
                description="Check system disk usage"
            )
        ])
        
        # Application health checks
        self.health_checks.extend([
            HealthCheck(
                name="response_time",
                check_function=self._check_response_time_health,
                critical=False,
                description="Check average response time"
            ),
            HealthCheck(
                name="error_rate",
                check_function=self._check_error_rate_health,
                critical=False,
                description="Check error rate"
            )
        ])
    
    def _initialize_default_alert_rules(self) -> None:
        """Initialize default alert rules"""
        
        self.alert_rules.extend([
            AlertRule(
                name="high_response_time",
                metric_name="response_time_default",
                threshold=5.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
                description="Average response time is too high"
            ),
            AlertRule(
                name="high_error_rate",
                metric_name="error_rate_percent",
                threshold=5.0,
                comparison="gt",
                duration_minutes=3,
                severity="critical",
                description="Error rate is too high"
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="system_memory_percent",
                threshold=85.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
                description="System memory usage is high"
            ),
            AlertRule(
                name="high_cpu_usage",
                metric_name="system_cpu_percent",
                threshold=90.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
                description="System CPU usage is high"
            )
        ])
    
    def _check_response_time_health(self) -> bool:
        """Check if response times are healthy"""
        recent_times = self._get_recent_metric_values("response_time_default", 10)
        if not recent_times:
            return True  # No data is not necessarily unhealthy
        
        avg_time = statistics.mean(recent_times)
        return avg_time < 10.0  # 10 second threshold
    
    def _check_error_rate_health(self) -> bool:
        """Check if error rate is healthy"""
        recent_errors = self._get_recent_metric_values("error_total", 10)
        recent_requests = self._get_recent_metric_values("request_total", 10)
        
        if not recent_requests:
            return True  # No requests is not unhealthy
        
        total_errors = sum(recent_errors) if recent_errors else 0
        total_requests = sum(recent_requests)
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        return error_rate < 10.0  # 10% threshold
    
    def _check_health_status(self) -> bool:
        """Check if health checks are passing"""
        health_status = self.get_health_status()
        return health_status["overall_status"] in ["healthy", "warning"]
    
    def _check_performance_thresholds(self) -> bool:
        """Check if performance is within acceptable thresholds"""
        metrics = self.get_performance_metrics(30)  # Last 30 minutes
        
        # Check response time
        if metrics["summary"]["avg_response_time"] > 5.0:
            return False
        
        # Check error rate
        if metrics["summary"]["error_rate_percent"] > 5.0:
            return False
        
        return True
    
    def _check_error_rates(self) -> bool:
        """Check if error rates are acceptable"""
        metrics = self.get_performance_metrics(60)  # Last hour
        return metrics["summary"]["error_rate_percent"] < 2.0
    
    def _check_resource_usage(self) -> bool:
        """Check if resource usage is normal"""
        system_metrics = self._get_system_metrics()
        
        return (system_metrics.get("cpu_percent", 0) < 80 and
                system_metrics.get("memory_percent", 0) < 80 and
                system_metrics.get("disk_percent", 0) < 90)
    
    def _check_dependencies(self) -> bool:
        """Check if external dependencies are available"""
        # This would check database connections, external APIs, etc.
        # For now, return True as a placeholder
        return True
    
    def _check_configuration(self) -> bool:
        """Check if configuration is valid"""
        # This would validate configuration settings
        # For now, return True as a placeholder
        return True
    
    def _get_production_recommendations(self, readiness_checks: Dict[str, bool]) -> List[str]:
        """Get recommendations for production readiness"""
        recommendations = []
        
        if not readiness_checks["health_checks_passing"]:
            recommendations.append("Fix failing health checks before deployment")
        
        if not readiness_checks["performance_acceptable"]:
            recommendations.append("Optimize performance to meet response time and throughput requirements")
        
        if not readiness_checks["error_rates_low"]:
            recommendations.append("Investigate and fix sources of errors")
        
        if not readiness_checks["resource_usage_normal"]:
            recommendations.append("Optimize resource usage or increase system capacity")
        
        if not readiness_checks["dependencies_available"]:
            recommendations.append("Ensure all external dependencies are available and configured")
        
        if not readiness_checks["configuration_valid"]:
            recommendations.append("Validate and fix configuration issues")
        
        if not readiness_checks["monitoring_active"]:
            recommendations.append("Start monitoring system before deployment")
        
        if not readiness_checks["alerts_configured"]:
            recommendations.append("Configure appropriate alert rules for production monitoring")
        
        if not recommendations:
            recommendations.append("System appears ready for production deployment")
        
        return recommendations


# Context manager for performance monitoring
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: ProductionMonitor, metric_name: str, tags: Dict[str, str] = None):
        self.monitor = monitor
        self.metric_name = metric_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            self.monitor.record_metric(
                self.metric_name,
                execution_time,
                MetricType.TIMER,
                self.tags
            )
            
            # Record error if exception occurred
            if exc_type:
                self.monitor.record_error(
                    error_type=exc_type.__name__,
                    error_message=str(exc_val),
                    context={"metric_name": self.metric_name, "tags": self.tags}
                )


# Global monitor instance
_global_monitor = None

def get_global_monitor() -> ProductionMonitor:
    """Get the global monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ProductionMonitor()
    return _global_monitor

def start_global_monitoring():
    """Start global monitoring"""
    monitor = get_global_monitor()
    monitor.start_monitoring()

def stop_global_monitoring():
    """Stop global monitoring"""
    monitor = get_global_monitor()
    monitor.stop_monitoring()