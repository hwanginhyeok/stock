"""Tesla delivery signal collectors — CPCA China and EU registration data.

수동 실행::

    python3 src/collectors/delivery/cpca_collector.py
    python3 src/collectors/delivery/eu_reg_collector.py
"""

from src.collectors.delivery.cpca_collector import CPCACollector
from src.collectors.delivery.eu_reg_collector import EURegistrationCollector

__all__ = ["CPCACollector", "EURegistrationCollector"]
