from sqlalchemy import create_engine, desc
from datetime import datetime
from models.db_models import MetricMeasurement
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger

logger = get_logger(__name__)

class MetricsReporter:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def get_latest_timestamp_metrics(self):
        """Get the most recent metrics for each unique metric name"""
        session = self.Session()
        try:
            logger.debug("Fetching latest timestamp metrics")
            
            # Get the latest timestamp for each metric name
            latest_metrics = session.query(
                MetricMeasurement.name,
                MetricMeasurement.value,
                MetricMeasurement.timestamp,
                MetricMeasurement.type_id,
                MetricMeasurement.unit_id
            ).order_by(
                MetricMeasurement.name,
                desc(MetricMeasurement.timestamp)
            ).distinct(MetricMeasurement.name).all()

            result = []
            for metric in latest_metrics:
                try:
                    metric_dict = {
                        'name': metric.name,
                        'value': float(metric.value),
                        'timestamp': metric.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'type': 'system'  # Default type
                    }
                    result.append(metric_dict)
                except Exception as e:
                    logger.error(f"Error processing metric {metric.name}: {str(e)}")
                    continue

            logger.debug(f"Returning {len(result)} metrics: {result}")
            return result

        except Exception as e:
            logger.error(f"Error getting latest timestamp metrics: {str(e)}")
            raise
        finally:
            session.close()

    def __del__(self):
        self.session.close()
