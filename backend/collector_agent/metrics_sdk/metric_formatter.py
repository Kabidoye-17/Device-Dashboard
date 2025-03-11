from typing import Dict, Any, List

from config.config import load_config, MetricConfig
from utils.timestamp import get_utc_timestamp, get_utc_offset
from utils.logger import get_logger
from collector_agent.metrics_sdk.dto import MeasurementDTO  

logger = get_logger('MetricFormatter')
config = load_config()

class MetricFormatter:
    def __init__(self):
        self.transform_rules = config.transform_rules
        self.crypto = config.collector_types.crypto

    def format(self, raw_metrics: List[Dict[str, Any]]) -> List[MeasurementDTO]:
        """
        Formats raw metrics into a list of MeasurementDTO objects based on the transform rules.

        Args:
            raw_metrics (List[Dict[str, Any]]): A list of raw metric dictionaries to be formatted.

        Returns:
            List[MeasurementDTO]: A list of formatted MeasurementDTO objects.
        """
        formatted_metrics = []
        
        for metric in raw_metrics:
            try:
                collector_type = metric.get('collector_type')
                if not collector_type:
                    logger.warning(f"Missing collector type in metric: {metric}")
                    continue

                # Get the corresponding transform rules for this collector type
                rules = getattr(self.transform_rules, collector_type, None)
                if not rules:
                    logger.warning(f"No transform rules found for collector: {collector_type}")
                    continue

                # Format each metric field according to its rules
                for field, rule in rules.__dict__.items():
                    if field in metric:
                        try:
                            name = rule.name
                            # Apply special formatting if specified in the rule
                            if rule.format:
                                name = name.format(**{k: metric[v] for k, v in rule.format.items()})
                            
                            measurement = MeasurementDTO(
                                device_id=metric['device_id'],
                                device_name=metric['device_name'],
                                name=name,
                                value=float(metric[field]),
                                type=collector_type,
                                unit=rule.unit,
                                timestamp_utc=get_utc_timestamp(),
                                utc_offset=get_utc_offset()
                            )

                            formatted_metrics.append(measurement)
                        except Exception as e:
                            logger.error(f"Error formatting field {field}: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing metric {metric}: {str(e)}")
                
        return formatted_metrics
