from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from models.db_models import Base, Device, MetricType, Unit, MetricMeasurement
from utils.logger import get_logger
import sqlalchemy as sa

logger = get_logger(__name__)

class DatabaseAggregator:
    def __init__(self, connection_string):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(connection_string, pool_recycle=280)  # Add pool_recycle for MySQL
            Base.metadata.create_all(self.engine)
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info("Database connection established successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def get_session(self):
        return self.Session()

    def cleanup_session(self, session):
        try:
            session.close()
            self.Session.remove()
        except Exception as e:
            logger.error(f"Error cleaning up session: {str(e)}")

    def verify_connection(self):
        """Verify database connection is working"""
        try:
            with self.engine.connect() as conn:
                conn.execute(sa.text('SELECT 1'))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False

    def get_or_create(self, model, filter_by, defaults={}):
        session = self.get_session()
        try:
            instance = session.query(model).filter_by(**filter_by).first()
            if instance:
                return instance  
            
            instance = model(**filter_by, **defaults)
            session.add(instance)
            session.commit()
            logger.debug(f"Created new {model.__name__}: {filter_by} {defaults}")
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error in get_or_create for {model.__name__}: {str(e)}")
            raise
        finally:
            session.expunge(instance)  # 🚀 Ensures instance is still usable
            self.cleanup_session(session)

            
    def store_metrics(self, metrics_data):
        session = self.get_session()
        try:
            logger.info(f"Storing {len(metrics_data)} metrics")
            for metric in metrics_data:
                logger.debug(f"Processing metric: {metric}")

                # Ensure metric value is valid
                try:
                    metric_value = float(metric['value'])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid metric value: {metric.get('value')}. Skipping.")
                    continue

                metric_type = self.get_or_create(
                    MetricType, 
                    filter_by={"name": str(metric.get("type", "system"))}
                )

                unit = self.get_or_create(
                    Unit, 
                    filter_by={"unit_name": str(metric.get("unit", "unknown"))}
                )

                device = self.get_or_create(
                    Device, 
                    filter_by={"device_id": str(metric.get("device_id", "unknown"))},
                    defaults={"device_name": str(metric.get("device_name", "unknown"))}
                )

                device = session.merge(device)  
                metric_type = session.merge(metric_type)  
                unit = session.merge(unit)  


                measurement = MetricMeasurement(
                    device_id=device.device_id,  
                    name=str(metric["name"]),
                    value=metric_value,
                    type_id=metric_type.id,
                    unit_id=unit.id,
                    timestamp=metric.get("timestamp")
                )
                session.add(measurement)

            session.commit()
            logger.info("Successfully stored all metrics")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error storing metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)


    