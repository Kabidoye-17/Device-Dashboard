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

            # Convert to JSON-serializable format with safe attribute access
            metrics_json = []
            for metric in latest_metrics:
                metric_dict = {
                    'id': metric.id,
                    'name': metric.name,
                    'value': float(metric.value),
                    'timestamp': metric.timestamp.isoformat(),
                    'device_id': metric.device_id
                }
                
                # Safely add optional attributes
                if hasattr(metric, 'unit') and metric.unit:
                    metric_dict['unit'] = metric.unit.unit_name
                if hasattr(metric, 'source') and metric.source:
                    metric_dict['source'] = metric.source.name

                metrics_json.append(metric_dict)

            logger.info(f"Retrieved {len(metrics_json)} metrics from timestamp {latest_timestamp}")
            return metrics_json

        except Exception as e:
            logger.error(f"Error fetching latest timestamp metrics: {str(e)}")
            raise

    def __del__(self):
        self.session.close()
