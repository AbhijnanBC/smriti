"""
engine/resolver.py — Dynamic ServiceResolver for Phase 9.

RECTIFIED: Replaces hardcoded if/elif chains with a dynamic registry.
Open/Closed: Adding a new service only requires registering it.
No changes to the resolver itself.
"""

from __future__ import annotations

import structlog
from smriti.exceptions import QueryPlanError

logger = structlog.get_logger(__name__)


class ServiceResolver:
    """
    Dynamically resolves a KnowledgeRequest to its execution service.

    Usage:
        resolver = ServiceResolver()
        resolver.register(ClaimRequest, query_service)
        resolver.register(SearchRequest, query_service)
        resolver.register(TraversalRequest, navigation_service)
        ...

        service = resolver.resolve(request)   # returns the matching service instance

    Principles:
        - Registry is mutable (can be extended at runtime).
        - Exact match on request type (no inheritance scanning).
        - Fails fast with a clear error if no service is registered.
    """

    def __init__(self) -> None:
        self._registry: dict[type, object] = {}

    def register(self, request_type: type, service_instance: object) -> None:
        """
        Register a service for a specific request type.

        Args:
            request_type: The KnowledgeRequest subclass (e.g., ClaimRequest).
            service_instance: The service that can handle this request type.
        """
        self._registry[request_type] = service_instance
        logger.debug("service registered", request_type=request_type.__name__)

    def resolve(self, request: object) -> object:
        """
        Return the service instance for the given request.

        Raises:
            QueryPlanError: If no service is registered for the request type.
        """
        service = self._registry.get(type(request))
        if service is None:
            raise QueryPlanError(
                f"No service registered for request type: {type(request).__name__}"
            )
        return service
