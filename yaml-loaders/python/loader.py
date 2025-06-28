#!/Users/shaneyost/.pyenv/shims/python3
import yaml


class EntityShip:
    yaml_tag = '!EntityShip'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node, deep=True)
        return cls(**data)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.to_dict())


class EntityName:
    yaml_tag = '!EntityName'

    def __init__(self, **kwargs):
        self.ships = {
            k: EntityShip.ensure(v)
            for k, v in kwargs.items()
        }

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.ships.items()}

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node, deep=True)
        return cls(**data)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.to_dict())


class EntityList:
    yaml_tag = '!EntityList'

    def __init__(self, **kwargs):
        self.entities = {
            k: EntityName.ensure(v)  # This ensures each value is an EntityName instance
            for k, v in kwargs.items()
        }

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.entities.items()}

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node, deep=True)
        return cls(**data)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.to_dict())


def ensure_class_factory(cls):
    def ensure(item):
        return item if isinstance(item, cls) else cls(**item)
    return ensure


EntityList.ensure = ensure_class_factory(EntityList)
EntityName.ensure = ensure_class_factory(EntityName)
EntityShip.ensure = ensure_class_factory(EntityShip)

yaml.add_constructor(EntityList.yaml_tag, EntityList.from_yaml)
yaml.add_constructor(EntityName.yaml_tag, EntityName.from_yaml)
yaml.add_constructor(EntityShip.yaml_tag, EntityShip.from_yaml)

yaml.add_representer(EntityList, EntityList.to_yaml)
yaml.add_representer(EntityName, EntityName.to_yaml)
yaml.add_representer(EntityShip, EntityShip.to_yaml)
