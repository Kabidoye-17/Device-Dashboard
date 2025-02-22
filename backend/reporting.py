from sqlalchemy import create_engine, func
from models.db_models import MetricMeasurement
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger

logger = get_logger(__name__)

class MetricsReporter:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_latest_timestamp_metrics(self):
        try:
  
            latest_timestamp = self.session.query(
                func.max(MetricMeasurement.timestamp)
            ).scalar()

            if not latest_timestamp:
                logger.warning("No metrics found in database")
                return []

            latest_metrics = self.session.query(MetricMeasurement).filter(
                MetricMeasurement.timestamp == latest_timestamp
            ).all()

            # Convert to JSON-serializable format
            metrics_json = []
            for metric in latest_metrics:
                metrics_json.append({
                    'id': metric.id,
                    'name': metric.name,
                    'value': float(metric.value),
                    'timestamp': metric.timestamp.isoformat(),
                    'device_id': metric.device_id,
                    'type': metric.metric_type.name if metric.metric_type else None,
                    'unit': metric.unit.unit_name if metric.unit else None,
                    'source': metric.source.name if metric.source else None
                })

            logger.info(f"Retrieved {len(metrics_json)} metrics from timestamp {latest_timestamp}")
            return metrics_json

        except Exception as e:
            logger.error(f"Error fetching latest timestamp metrics: {str(e)}")
            raise

    def __del__(self):
        self.session.close()
