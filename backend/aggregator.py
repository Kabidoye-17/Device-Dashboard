from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from models.db_models import Base, Device, MetricType, Unit, MetricMeasurement, DeviceDetails
from utils.logger import get_logger
import sqlalchemy as sa

logger = get_logger(__name__)

class DatabaseAggregator:
    def __init__(self, connection_string):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(connection_string, pool_recycle=280)
            self.Session = scoped_session(sessionmaker(bind=self.engine))

            inspector = inspect(self.engine)
            if not inspector.get_table_names():
                Base.metadata.create_all(self.engine)
                logger.info("Database tables created successfully")
            else:
                logger.info("Database tables already exist")

            logger.info("Database connection established successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def __enter__(self):
        self.session = self.get_session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.cleanup_session(self.session)

    def get_session(self):
        return self.Session()

    def cleanup_session(self, session):
        try:
            self.Session.remove()
        except Exception as e:
            logger.error(f"Error cleaning up session: {str(e)}")

    def get_or_create(self, session, model, filter_by, defaults={}, cache=None):
        if cache is not None:
            cache_key = tuple(sorted(filter_by.items()))  # Ensuring consistent order
            if cache_key in cache:
                return cache[cache_key]

        try:
            instance = session.query(model).filter_by(**filter_by).first()
            if instance:
                return instance

            instance = model(**filter_by, **defaults)
            session.add(instance)
            session.flush()  # Ensures instance is persisted before returning
            logger.debug(f"Created new {model.__name__}: {filter_by} {defaults}")
            
            if cache is not None:
                cache[cache_key] = instance
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error in get_or_create for {model.__name__}: {str(e)}")
            raise

    def store_metrics(self, metrics_data):
        with self as session:
            try:
                logger.info(f"Storing {len(metrics_data)} metrics")

                metric_type_cache = {}
                unit_cache = {}
                device_cache = {}
                device_details_cache = {}
                measurements = []

                for metric in metrics_data:
                    logger.debug(f"Processing metric: {metric.get('name', 'Unknown')}, Value: {metric.get('value', 'N/A')}")
                    
                    metric_value = self._validate_metric_value(metric)
                    if metric_value is None:
                        continue

                    metric_type = self._get_or_create_cached(session, MetricType, {"name": str(metric.get("type", "system"))}, metric_type_cache)
                    unit = self._get_or_create_cached(session, Unit, {"unit_name": str(metric.get("unit", "unknown"))}, unit_cache)
                    device = self._get_or_create_cached(session, Device, {"device_id": str(metric.get("device_id", "unknown"))}, device_cache)
                    
                    self._get_or_create_cached(session, DeviceDetails, {"device_id": device.device_id}, device_details_cache,
                        defaults={"device_name": str(metric.get("device_name", "unknown"))})

                    measurements.append(self._prepare_measurement(metric, device, metric_type, unit, metric_value))

                self._bulk_insert_measurements(session, measurements)
                return True

            except Exception as e:
                session.rollback()
                logger.error(f"Error storing metrics: {str(e)}")
                raise

    def _validate_metric_value(self, metric):
        try:
            return float(metric['value'])
        except (ValueError, TypeError):
            logger.warning(f"Invalid metric value: {metric.get('value')}. Skipping.")
            return None

    def _get_or_create_cached(self, session, model, filter_by, cache, defaults={}):
        return self.get_or_create(session, model, filter_by, defaults, cache)

    def _prepare_measurement(self, metric, device, metric_type, unit, metric_value):
        return MetricMeasurement(
            device_id=device.device_id,
            name=str(metric["name"]),
            value=metric_value,
            type_id=metric_type.id,
            unit_id=unit.id,
            timestamp_utc=metric.get("timestamp_utc"),
            utc_offset=metric.get("utc_offset")
        )

    def _bulk_insert_measurements(self, session, measurements):
        if measurements:
            try:
                session.bulk_save_objects(measurements)
                session.commit()
                logger.info("Successfully stored all metrics")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Bulk insert failed: {str(e)}")
                raise
