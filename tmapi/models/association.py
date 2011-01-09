from tmapi.exceptions import ModelConstraintException

from construct_fields import ConstructFields
from reifiable import Reifiable
from role import Role
from scoped import Scoped
from topic import Topic
from typed import Typed


class Association (ConstructFields, Reifiable, Scoped, Typed):
    
    class Meta:
        app_label = 'tmapi'

    def create_role (self, role_type, player):
        """Creates a new role representing a role in this association.

        :param role_type: the role type
        :type role_type: `Topic`
        :param player: the role player
        :type player: `Topic`
        :rtype: `Role`

        """
        if role_type is None or player is None:
            raise ModelConstraintException
        role = Role(association=self, type=role_type, player=player,
                    topic_map=self.topic_map)
        role.save()
        return role

    def get_parent (self):
        """Returns the `TopicMap` to which this association belongs.

        :rtype: `TopicMap`

        """
        return self.topic_map
        
    def get_roles (self, role_type=None):
        """Returns the `Role`s participating in this association.

        If `role_type` is not None, returns all roles with the
        specified type.

        :param role_type: the type of the `Role` instances to be returned
        :type role_type: `Topic`
        :rtype: `QuerySet` of `Role`s
        
        """
        if role_type is None:
            roles = self.roles.all()
        else:
            roles = self.roles.filter(type=role_type)
        return roles

    def get_role_types (self):
        """Returns the role types participating in this association.

        :rtype: `QuerySet` of `Topic`s

        """
        return Topic.objects.filter(typed_roles__association=self).distinct()