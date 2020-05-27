"""
Helper that handles registration and deregistration of auto scaling for DynamoDB
tables and indexes.
"""
import logging
from typing import Iterable, Optional

from dynamo_query.dynamo_query_types import (
    ApplicationAutoScalingClient,
    MetricTypeTypeDef,
    ScalableDimensionTypeDef,
    TargetTrackingScalingPolicyConfigurationTypeDef,
)
from dynamo_query.dynamo_table_index import DynamoTableIndex


class DynamoAutoscaler:
    """
    Helper that handles registration and deregistration of auto scaling for DynamoDB
    tables and indexes.

    Arguments:
        client -- Boto3 ApplicationAutoscaling client,
        logger -- `logging.Logger` instance.
    """

    SCALE_TARGET_VALUE = 50.0  # percent
    SCALE_OUT_COOLDOWN = 60  # seconds
    SCALE_IN_COOLDOWN = 120  # seconds

    SCALE_MIN_CAPACITY = 50
    SCALE_MAX_CAPACITY = 40000

    def __init__(
        self, client: ApplicationAutoScalingClient, logger: Optional[logging.Logger] = None,
    ) -> None:
        self.client: ApplicationAutoScalingClient = client
        self._lazy_logger = logger

    @property
    def _logger(self) -> logging.Logger:
        if self._lazy_logger is None:
            self._lazy_logger = logging.Logger(__name__)

        return self._lazy_logger

    def deregister_auto_scaling(
        self, table_name: str, global_secondary_indexes: Iterable[DynamoTableIndex] = (),
    ) -> None:
        """
        Deregister auto scaling for table.

        Arguments:
            table_name -- Name of the table
            global_secondary_indexes -- Indexes that should have autoscaling disabled
        """
        for gsi in global_secondary_indexes:
            self.deregister_scalable_target(
                table_name=table_name,
                scalable_dimension="dynamodb:index:ReadCapacityUnits",
                index_name=gsi.name,
            )
            self.deregister_scalable_target(
                table_name=table_name,
                scalable_dimension="dynamodb:index:WriteCapacityUnits",
                index_name=gsi.name,
            )

        self.deregister_scalable_target(
            table_name=table_name, scalable_dimension="dynamodb:table:ReadCapacityUnits",
        )
        self.deregister_scalable_target(
            table_name=table_name, scalable_dimension="dynamodb:table:WriteCapacityUnits",
        )

    def register_auto_scaling(
        self,
        table_name: str,
        global_secondary_indexes: Iterable[DynamoTableIndex] = (),
        min_capacity: int = SCALE_MIN_CAPACITY,
        max_capacity: int = SCALE_MAX_CAPACITY,
    ) -> None:
        """
        Register auto scaling for table.

        Arguments:
            table_name -- Name of the table
            global_secondary_indexes -- Indexes that should also have autoscaling
            min_capacity -- MinCapacity for table and indexes
            max_capacity -- MaxCapacity for table and indexes
        """
        self._logger.debug(f"Registering Read scalable target for {table_name} table")
        self.register_scalable_target(
            table_name,
            scalable_dimension="dynamodb:table:ReadCapacityUnits",
            min_capacity=min_capacity,
            max_capacity=max_capacity,
        )
        self.put_scaling_policy(
            table_name,
            scalable_dimension="dynamodb:table:ReadCapacityUnits",
            scaling_policy_configs=self.create_scaling_policy_configs(
                "DynamoDBReadCapacityUtilization"
            ),
        )

        self._logger.debug(f"Registering Write scalable target for {table_name} table")
        self.register_scalable_target(
            table_name,
            scalable_dimension="dynamodb:table:WriteCapacityUnits",
            min_capacity=min_capacity,
            max_capacity=max_capacity,
        )
        self.put_scaling_policy(
            table_name,
            scalable_dimension="dynamodb:table:WriteCapacityUnits",
            scaling_policy_configs=self.create_scaling_policy_configs(
                "DynamoDBWriteCapacityUtilization"
            ),
        )

        # For GSIs
        for gsi in global_secondary_indexes:
            self._logger.debug(
                f"Registering Read scalable target for {table_name} table index {gsi.name}"
            )
            self.register_scalable_target(
                table_name,
                scalable_dimension="dynamodb:index:ReadCapacityUnits",
                index_name=gsi.name,
                min_capacity=min_capacity,
                max_capacity=max_capacity,
            )
            self.put_scaling_policy(
                table_name,
                index_name=gsi.name,
                scalable_dimension="dynamodb:index:ReadCapacityUnits",
                scaling_policy_configs=self.create_scaling_policy_configs(
                    "DynamoDBReadCapacityUtilization"
                ),
            )

            self._logger.debug(
                f"Registering Write scalable target for {table_name} table index {gsi.name}"
            )
            self.register_scalable_target(
                table_name,
                scalable_dimension="dynamodb:index:WriteCapacityUnits",
                index_name=gsi.name,
                min_capacity=min_capacity,
                max_capacity=max_capacity,
            )
            self.put_scaling_policy(
                table_name,
                index_name=gsi.name,
                scalable_dimension="dynamodb:index:WriteCapacityUnits",
                scaling_policy_configs=self.create_scaling_policy_configs(
                    "DynamoDBWriteCapacityUtilization"
                ),
            )

    def deregister_scalable_target(
        self,
        table_name: str,
        scalable_dimension: ScalableDimensionTypeDef,
        index_name: Optional[str] = None,
    ) -> None:
        """
        Deregister scalable table or index.

        Arguments:
            table_name -- the name of the table
            scalable_dimension -- scalable dimension name
            index_name -- the name of the index. If provided - deregiters policy for index
        """
        resource_id = f"table/{table_name}"
        if index_name is not None:
            resource_id = f"table/{table_name}/index/{index_name}"

        self.client.deregister_scalable_target(
            ServiceNamespace="dynamodb",
            ResourceId=resource_id,
            ScalableDimension=scalable_dimension,
        )

    def register_scalable_target(
        self,
        table_name: str,
        scalable_dimension: ScalableDimensionTypeDef,
        index_name: Optional[str] = None,
        min_capacity: int = SCALE_MIN_CAPACITY,
        max_capacity: int = SCALE_MAX_CAPACITY,
    ) -> None:
        """
        Register scalable table or index.

        Arguments:
            table_name -- Name of the table
            scalable_dimension -- Scalable dimension name
            index_name -- Name of the index. If provided - adds policy for index
            min_capacity -- MinCapacity
            max_capacity -- MaxCapacity
        """
        resource_id = f"table/{table_name}"
        if index_name is not None:
            resource_id = f"table/{table_name}/index/{index_name}"

        self.client.register_scalable_target(
            ServiceNamespace="dynamodb",
            ResourceId=resource_id,
            ScalableDimension=scalable_dimension,
            MinCapacity=min_capacity,
            MaxCapacity=max_capacity,
        )

    @staticmethod
    def create_scaling_policy_configs(
        metric_type: MetricTypeTypeDef,
        target_value: float = SCALE_TARGET_VALUE,
        scale_out_cooldown: int = SCALE_OUT_COOLDOWN,
        scale_in_cooldown: int = SCALE_IN_COOLDOWN,
    ) -> TargetTrackingScalingPolicyConfigurationTypeDef:
        """
        Create auto scaling policy dict.

        Arguments:
            metric_type -- DynamoDB Metric type
            target_value -- Percent of use to aim for
            scale_out_cooldown -- Scale out cooldown in seconds
            scale_in_cooldown -- Scale in cooldown in seconds

        Returns:
            Scaling policy configs to use in put_scaling_policy
        """
        return {
            "TargetValue": target_value,
            "PredefinedMetricSpecification": {"PredefinedMetricType": metric_type},
            "ScaleOutCooldown": scale_out_cooldown,
            "ScaleInCooldown": scale_in_cooldown,
        }

    def put_scaling_policy(
        self,
        table_name: str,
        scalable_dimension: ScalableDimensionTypeDef,
        scaling_policy_configs: TargetTrackingScalingPolicyConfigurationTypeDef,
        index_name: Optional[str] = None,
    ) -> None:
        """
        Add scaling policy for table or for index.

        Arguments:
            table_name -- Name of the table
            scalable_dimension -- Scalable dimension name
            scaling_policy_configs -- Scaling policy configs from AWS docs
            index_name -- Name of the index. If provided - adds policy for index
        """
        resource_id = f"table/{table_name}"
        if index_name:
            resource_id = f"table/{table_name}/index/{index_name}"

        self.client.put_scaling_policy(
            ServiceNamespace="dynamodb",
            ResourceId=resource_id,
            PolicyType="TargetTrackingScaling",
            PolicyName="ScaleDynamoDBReadCapacityUtilization",
            ScalableDimension=scalable_dimension,
            TargetTrackingScalingPolicyConfiguration=scaling_policy_configs,
        )
