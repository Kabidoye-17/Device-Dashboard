from sqlalchemy import create_engine, desc
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
            
            # Get the latest timestamp
            subquery = session.query(
                MetricMeasurement.name,
                desc(MetricMeasurement.timestamp)
            ).group_by(
                MetricMeasurement.name
            ).subquery()

            # Get the full metrics data for the latest timestamp
            metrics = session.query(MetricMeasurement).filter(
                (MetricMeasurement.name == subquery.c.name) &
                (MetricMeasurement.timestamp == subquery.c.timestamp)
            ).all()

            result = [
                {
                    'name': metric.name,
                    'value': float(metric.value),  # Ensure numeric values
                    'timestamp': metric.timestamp.isoformat(),  # ISO format timestamp
                    'type': metric.type.name if metric.type else 'unknown',
                    'unit': metric.unit.unit_name if metric.unit else 'unknown'
                }
                for metric in metrics
            ]
            
            logger.debug(f"Returning {len(result)} metrics: {result}")
            return result

        except Exception as e:
            logger.error(f"Error getting latest timestamp metrics: {str(e)}")
            raise
        finally:
            session.close()

    def __del__(self):
        self.session.close()
