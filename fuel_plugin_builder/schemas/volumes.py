from fuel_plugin_builder import validators


class SchemaVolumesV3_0_0(object):

    @property
    def volume_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['volumes_roles_mapping', 'volumes'],
            'properties': {
                'volumes_roles_mapping': {
                    'type': 'object',
                    'patternProperties': {
                        validators.schemas.schema_task_v2_1_0.task_name_pattern: {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'description': 'Volume allocations for role',
                                'required': ['allocate_size', 'id'],
                                'properties': {
                                    'allocate_size': {
                                        'type': 'string',
                                        'enum': ['all', 'min', 'full-disk']
                                    },
                                    'id': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'additionalProperties': False
                },
                'volumes': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['id', 'type'],
                        'properties': {
                            'id': {
                                'type': 'string'
                            },
                            'type': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }

volumes_v3_0_0 = SchemaVolumesV3_0_0()
