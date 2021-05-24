# DynamoAutoscaler

> Auto-generated documentation for [dynamo_query.dynamo_autoscaler](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py) module.

Helper that handles registration and deregistration of auto scaling for DynamoDB
tables and indexes.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoAutoscaler
    - [DynamoAutoscaler](#dynamoautoscaler)
        - [DynamoAutoscaler.create_scaling_policy_configs](#dynamoautoscalercreate_scaling_policy_configs)
        - [DynamoAutoscaler().deregister_auto_scaling](#dynamoautoscalerderegister_auto_scaling)
        - [DynamoAutoscaler().deregister_scalable_target](#dynamoautoscalerderegister_scalable_target)
        - [DynamoAutoscaler().put_scaling_policy](#dynamoautoscalerput_scaling_policy)
        - [DynamoAutoscaler().register_auto_scaling](#dynamoautoscalerregister_auto_scaling)
        - [DynamoAutoscaler().register_scalable_target](#dynamoautoscalerregister_scalable_target)

## DynamoAutoscaler

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L17)

```python
class DynamoAutoscaler():
    def __init__(
        client: ApplicationAutoScalingClient,
        logger: Optional[logging.Logger] = None,
    ) -> None:
```

Helper that handles registration and deregistration of auto scaling for DynamoDB
tables and indexes.

#### Arguments

- `client` - Boto3 ApplicationAutoscaling client,
- `logger` - `logging.Logger` instance.

#### See also

- [ApplicationAutoScalingClient](dynamo_query_types.md#applicationautoscalingclient)

### DynamoAutoscaler.create_scaling_policy_configs

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L222)

```python
@staticmethod
def create_scaling_policy_configs(
    metric_type: MetricTypeTypeDef,
    target_value: float = SCALE_TARGET_VALUE,
    scale_out_cooldown: int = SCALE_OUT_COOLDOWN,
    scale_in_cooldown: int = SCALE_IN_COOLDOWN,
) -> TargetTrackingScalingPolicyConfigurationTypeDef:
```

Create auto scaling policy dict.

#### Arguments

- `metric_type` - DynamoDB Metric type
- `target_value` - Percent of use to aim for
- `scale_out_cooldown` - Scale out cooldown in seconds
- `scale_in_cooldown` - Scale in cooldown in seconds

#### Returns

Scaling policy configs to use in put_scaling_policy

#### See also

- [MetricTypeTypeDef](dynamo_query_types.md#metrictypetypedef)
- [TargetTrackingScalingPolicyConfigurationTypeDef](dynamo_query_types.md#targettrackingscalingpolicyconfigurationtypedef)

### DynamoAutoscaler().deregister_auto_scaling

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L49)

```python
def deregister_auto_scaling(
    table_name: str,
    global_secondary_indexes: Iterable[DynamoTableIndex] = (),
) -> None:
```

Deregister auto scaling for table.

#### Arguments

- `table_name` - Name of the table
- `global_secondary_indexes` - Indexes that should have autoscaling disabled

### DynamoAutoscaler().deregister_scalable_target

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L168)

```python
def deregister_scalable_target(
    table_name: str,
    scalable_dimension: ScalableDimensionTypeDef,
    index_name: Optional[str] = None,
) -> None:
```

Deregister scalable table or index.

#### Arguments

- `table_name` - the name of the table
- `scalable_dimension` - scalable dimension name
- `index_name` - the name of the index. If provided - deregiters policy for index

#### See also

- [ScalableDimensionTypeDef](dynamo_query_types.md#scalabledimensiontypedef)

### DynamoAutoscaler().put_scaling_policy

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L248)

```python
def put_scaling_policy(
    table_name: str,
    scalable_dimension: ScalableDimensionTypeDef,
    scaling_policy_configs: TargetTrackingScalingPolicyConfigurationTypeDef,
    index_name: Optional[str] = None,
) -> None:
```

Add scaling policy for table or for index.

#### Arguments

- `table_name` - Name of the table
- `scalable_dimension` - Scalable dimension name
- `scaling_policy_configs` - Scaling policy configs from AWS docs
- `index_name` - Name of the index. If provided - adds policy for index

#### See also

- [ScalableDimensionTypeDef](dynamo_query_types.md#scalabledimensiontypedef)
- [TargetTrackingScalingPolicyConfigurationTypeDef](dynamo_query_types.md#targettrackingscalingpolicyconfigurationtypedef)

### DynamoAutoscaler().register_auto_scaling

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L82)

```python
def register_auto_scaling(
    table_name: str,
    global_secondary_indexes: Iterable[DynamoTableIndex] = (),
    min_capacity: int = SCALE_MIN_CAPACITY,
    max_capacity: int = SCALE_MAX_CAPACITY,
) -> None:
```

Register auto scaling for table.

#### Arguments

- `table_name` - Name of the table
- `global_secondary_indexes` - Indexes that should also have autoscaling
- `min_capacity` - MinCapacity for table and indexes
- `max_capacity` - MaxCapacity for table and indexes

### DynamoAutoscaler().register_scalable_target

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_autoscaler.py#L192)

```python
def register_scalable_target(
    table_name: str,
    scalable_dimension: ScalableDimensionTypeDef,
    index_name: Optional[str] = None,
    min_capacity: int = SCALE_MIN_CAPACITY,
    max_capacity: int = SCALE_MAX_CAPACITY,
) -> None:
```

Register scalable table or index.

#### Arguments

- `table_name` - Name of the table
- `scalable_dimension` - Scalable dimension name
- `index_name` - Name of the index. If provided - adds policy for index
- `min_capacity` - MinCapacity
- `max_capacity` - MaxCapacity

#### See also

- [ScalableDimensionTypeDef](dynamo_query_types.md#scalabledimensiontypedef)
