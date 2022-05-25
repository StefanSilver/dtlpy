import json
import warnings
from enum import Enum
from .. import repositories


class Role(str, Enum):
    OWNER = "owner",
    ADMIN = "admin",
    MEMBER = "member",
    ANNOTATOR = "annotator",
    DEVELOPER = "engineer",
    ANNOTATION_MANAGER = "annotationManager"
    ALL = "*"


class PlatformEntityType(str, Enum):
    USER = "user",
    TASK = "task",
    PROJECT = "project",
    ORG = "org",
    DATASET = "dataset"
    DATALOOP = "DATALOOP"


class SettingsValueTypes(str, Enum):
    BOOLEAN = "boolean",
    NUMBER = "number",
    SELECT = "select",
    MULTI_SELECT = "multi-select"


class SettingsTypes(str, Enum):
    FEATURE_FLAG = "feature_flag",
    USER_SETTINGS = "user_settings"


class SettingsSectionNames(str, Enum):
    ACCOUNT = "Account",
    CONTACT = "Contact",
    APPLICATIONS = "Applications",
    STUDIO = "Studio",
    PLATFORM = "Platform"
    SDK = "SDK"


class SettingScope:
    def __init__(
            self,
            type: PlatformEntityType,
            id: str,
            role: Role,
            prevent_override: bool,
            visible: bool,
    ):
        self.type = type
        self.id = id
        self.role = role
        self.prevent_override = prevent_override
        self.visible = visible

    @staticmethod
    def from_json(_json):
        return SettingScope(
            type=_json.get('type', None),
            id=_json.get('id', None),
            role=_json.get('role', None),
            prevent_override=_json.get('preventOverride', None),
            visible=_json.get('visible', None)
        )

    def to_json(self):
        _json = dict()

        if self.type:
            _json['type'] = self.type
        if self.id:
            _json['id'] = self.id
        if self.role:
            _json['role'] = self.role
        if self.prevent_override:
            _json['preventOverride'] = self.prevent_override
        if self.visible:
            _json['visible'] = self.visible

        return _json


class BaseSetting:

    def __init__(
            self,
            default_value,
            value,
            name: str,
            value_type: SettingsValueTypes,
            scope: SettingScope,
            metadata: dict,
            setting_type: SettingsTypes,
            id: str = None,
            client_api=None,
            project=None,
            org=None
    ):
        if value is None and default_value is None:
            raise Exception('Must provide either value or default_value')

        self.default_value = default_value
        self.name = name
        self.value = value
        self.value_type = value_type
        self.scope = scope
        self.metadata = metadata
        self.setting_type = setting_type
        self.client_api = client_api
        self.project = project
        self.org = org
        self.id = id
        self.settings = repositories.Settings(client_api=self.client_api, project=self.project, org=self.org)

    @staticmethod
    def from_json(_json: dict, client_api, project=None, org=None):
        scope = SettingScope.from_json(_json.get('scope', None))
        return BaseSetting(
            default_value=_json.get('defaultValue', None),
            name=_json.get('name', None),
            value=_json.get('value', None),
            value_type=_json.get('valueType', None),
            scope=scope,
            metadata=_json.get('metadata', None),
            id=_json.get('id', None),
            setting_type=_json.get('settingType', None),
            client_api=client_api,
            project=project,
            org=org
        )

    @staticmethod
    def __slot_to_db_slot(slot: dict):
        if 'displayScopes' in slot:
            scopes = slot['displayScopes']
            if scopes:
                for display_scope in scopes:
                    if 'filter' in display_scope and isinstance(display_scope['filter'], dict):
                        display_scope['filter'] = json.dumps(display_scope['filter'])

    def to_json(self):
        if self.metadata is not None and 'slots' in self.metadata and isinstance(self.metadata['slots'], list):
            for slot in self.metadata['slots']:
                self.__slot_to_db_slot(slot)

        _json = {
            'name': self.name,
            'valueType': self.value_type,
            'scope': self.scope.to_json(),
            'settingType': self.setting_type,
            'id': self.id
        }

        if self.metadata is not None:
            _json['metadata'] = self.metadata

        if self.value is not None:
            _json['value'] = self.value

        if self.default_value is not None:
            _json['defaultValue'] = self.default_value

        return _json

    def delete(self):
        """
        Delete a setting

        :return: True if success exceptions if not
        """
        return self.settings.delete(setting_id=self.id)

    def update(self):
        """
        Update a setting

        :return: setting entity
        """
        return self.settings.update(setting=self)


class Setting(BaseSetting):
    def __init__(
            self,
            value,
            name: str,
            value_type: SettingsValueTypes,
            scope: SettingScope,
            section_name: SettingsSectionNames,
            default_value=None,
            inputs=None,
            metadata: dict = None,
            description: str = None,
            icon: str = None,
            id: str = None,
            sub_section_name: str = None,
            hint=None,
            client_api=None,
            project=None,
            org=None
    ):
        super().__init__(
            default_value=default_value,
            value=value,
            name=name,
            value_type=value_type,
            scope=scope,
            metadata=metadata,
            setting_type=SettingsTypes.USER_SETTINGS,
            client_api=client_api,
            project=project,
            org=org,
            id=id
        )
        self.description = description
        self.inputs = inputs
        self.icon = icon
        self.section_name = section_name
        self.hint = hint
        self.sub_section_name = sub_section_name

    @staticmethod
    def from_json(_json: dict, client_api, project=None, org=None):
        scope = SettingScope.from_json(_json.get('scope', None))
        return Setting(
            default_value=_json.get('defaultValue', None),
            name=_json.get('name', None),
            value=_json.get('value', None),
            value_type=_json.get('valueType', None),
            scope=scope,
            metadata=_json.get('metadata', None),
            description=_json.get('description', None),
            inputs=_json.get('inputs', None),
            icon=_json.get('icon', None),
            section_name=_json.get('sectionName', None),
            hint=_json.get('hint', None),
            sub_section_name=_json.get('subSectionName', None),
            id=_json.get('id', None),
            client_api=client_api,
            project=project,
            org=org
        )

    def to_json(self):
        _json = super().to_json()
        if self.description is not None:
            _json['description'] = self.description
        if self.inputs is not None:
            _json['inputs'] = self.inputs
        if self.icon is not None:
            _json['icon'] = self.icon
        if self.section_name is not None:
            _json['sectionName'] = self.section_name
        if self.hint is not None:
            _json['hint'] = self.hint
        if self.sub_section_name is not None:
            _json['subSectionName'] = self.sub_section_name
        if self.id is not None:
            _json['id'] = self.id
        return _json


class UserSetting(Setting):
    def __init__(
            self,
            default_value,
            value,
            name: str,
            value_type: SettingsValueTypes,
            scope: SettingScope,
            section_name: SettingsSectionNames,
            inputs=None,
            metadata: dict = None,
            description: str = None,
            icon: str = None,
            id: str = None,
            sub_section_name: str = None,
            hint=None,
            client_api=None,
            project=None,
            org=None
    ):
        warnings.warn(
            message='UserSetting will be Deprecation from version 1.62 use Setting',
            category=DeprecationWarning)
        super().__init__(
            default_value=default_value,
            value=value,
            name=name,
            value_type=value_type,
            scope=scope,
            metadata=metadata,
            client_api=client_api,
            project=project,
            org=org,
            id=id,
            section_name=section_name,
            inputs=inputs,
            description=description,
            icon=icon,
            sub_section_name=sub_section_name,
            hint=hint
        )
