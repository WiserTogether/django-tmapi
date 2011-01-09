from django.db import models

from tmapi.exceptions import ModelConstraintException

from association import Association
from item_identifier import ItemIdentifier
from locator import Locator
from reifiable import Reifiable
from subject_identifier import SubjectIdentifier
from subject_locator import SubjectLocator
from topic import Topic


class TopicMap (Reifiable):

    """Represents a topic map item."""

    # item_identifiers duplicates that defined in construct_fields.py.
    item_identifiers = models.ManyToManyField('ItemIdentifier',
                                              related_name='topic_map')
    iri = models.CharField(max_length=512)
    title = models.CharField(max_length=128, blank=True)
    base_address = models.CharField(max_length=512, blank=True)

    class Meta:
        app_label = 'tmapi'

    def create_association (self, association_type, scope=None):
        """Creates an `Association` in this topic map with the
        specified type and scope.

        :param association_type: the association type
        :type association_type: `Topic`
        :param scope: list of `Topic`s
        :rtype: `Association`

        """
        if association_type is None:
            raise ModelConstraintException
        association = Association(type=association_type, topic_map=self)
        association.save()
        if scope is None:
            scope = []
        for topic in scope:
            association.scope.add(topic)
        return association
        
    def create_locator (self, reference):
        """Returns a `Locator` instance representing the specified IRI
        reference.

        The specified IRI reference is assumed to be absolute.

        :param reference: a string which uses the IRI notation
        :type reference: string
        :rtype: `Locator`

        """
        return Locator(reference)
        
    def create_topic (self):
        """Returns a `Topic` instance with an automatically generated
        item identifier.

        This method returns never an existing `Topic` but creates a
        new one with an automatically generated item identifier.

        Returns the newly created `Topic` instance with an automatically
        generated item identifier.

        :rtype: `Topic`

        """
        topic = Topic(topic_map=self)
        # QAZ: add automatically generated item identifier.
        topic.save()
        return topic

    def create_topic_by_item_identifier (self, item_identifier):
        """Returns a `Topic` instance with the specified item identifier.

        This method returns either an existing `Topic` or creates a
        new `Topic` instance with the specified item identifier.

        If a topic with the specified item identifier exists in the
        topic map, that topic is returned. If a topic with a subject
        identifier equal to the specified item identifier exists, the
        specified item identifier is added to that topic and the topic
        is returned. If neither a topic with the specified item
        identifier nor with a subject identifier equal to the subject
        identifier exists, a topic with the item identifier is
        created.

        :param item_identifier: the item identifier the topic should contain
        :type item_identifier: `Locator`
        :rtype: `Topic`

        """
        if item_identifier is None:
            raise ModelConstraintException
        reference = item_identifier.to_external_form()
        try:
            topic = self.topic_constructs.get(
                item_identifiers__address=reference)
        except Topic.DoesNotExist:
            try:
                topic = self.topic_constructs.get(
                    subject_identifiers__address=reference)
            except Topic.DoesNotExist:
                topic = Topic(topic_map=self)
                topic.save()
            ii = ItemIdentifier(address=reference, containing_topic_map=self)
            ii.save()
            topic.item_identifiers.add(ii)
        return topic            
    
    def create_topic_by_subject_identifier (self, subject_identifier):
        """Returns a `Topic` instance with the specified subject identifier.

        This method returns either an existing `Topic` or creates a
        new `Topic` instance with the specified subject identifier.

        If a topic with the specified subject identifier exists in
        this topic map, that topic is returned. If a topic with an
        item identifier equal to the specified subject identifier
        exists, the specified subject identifier is added to that
        topic and the topic is returned. If neither a topic with the
        specified subject identifier nor with an item identifier equal
        to the subject identifier exists, a topic with the subject
        identifier is created.

        :param subject_identifier: the subject identifier the topic
          should contain
        :type subject_identifier: `Locator`
        :rtype: `Topic`

        """
        if subject_identifier is None:
            raise ModelConstraintException
        reference = subject_identifier.to_external_form()
        try:
            topic = self.topic_constructs.get(
                subject_identifiers__address=reference)
        except Topic.DoesNotExist:
            try:
                topic = self.topic_constructs.get(
                    item_identifiers__address=reference)
            except Topic.DoesNotExist:
                topic = Topic(topic_map=self)
                topic.save()
            si = SubjectIdentifier(topic=topic, address=reference)
            si.save()
            topic.subject_identifiers.add(si)
        return topic

    def create_topic_by_subject_locator (self, subject_locator):
        """Returns a `Topic` instance with the specified subject locator.

        This method returns either an existing `Topic` or creates a
        new `Topic` instance with the specified subject locator.

        :param subject_locator: the subject locator the topic should
          contain
        :type subject_locator: `Locator`
        :rtype: `Topic`

        """
        if subject_locator is None:
            raise ModelConstraintException
        reference = subject_locator.to_external_form()
        try:
            topic = self.topic_constructs.get(
                subject_locators__address=reference)
        except Topic.DoesNotExist:
            topic = Topic(topic_map=self)
            topic.save()
            sl = SubjectLocator(topic=topic, address=reference)
            sl.save()
            topic.subject_locators.add(sl)
        return topic

    def get_associations (self):
        """Returns all `Association`s contained in this topic map.

        :rtype: `QuerySet` of `Association`s

        """
        return self.association_constructs.all()

    def get_construct_by_item_identifier (self, item_identifier):
        """Returns a `Construct` by its item identifier.

        :param item_identifier: the item identifier of the construct
          to be returned
        :type item_identifier: `Locator`
        :rtype: a construct or None

        """
        address = item_identifier.to_external_form()
        try:
            ii = ItemIdentifier.objects.get(address=address,
                                            containing_topic_map=self)
            construct = ii.get_construct()
        except ItemIdentifier.DoesNotExist:
            construct = None
        return construct
    
    def get_locator (self):
        """Returns the `Locator` that was used to create the topic map.

        Note: The returned locator represents the storage address of
        the topic map and implies no further semantics.

        :rtype: `Locator`

        """
        return Locator(self.iri)
    
    def get_parent (self):
        """Returns None.

        :rtype: None

        """
        return None

    def get_topics (self):
        """Returns all `Topic`s contained in this topic map.

        :rtype: `QuerySet` of `Topic`s

        """
        return self.topic_constructs.all()

    def get_topic_by_subject_identifier (self, subject_identifier):
        """Returns a topic by its subject identifier.

        If no topic with the specified subject identifier exists, this
        method returns `None`.

        :param subject_identifier: the subject identifier of the topic
          to be returned
        :type subject_identifier: `Locator`
        :rtype: `Topic` or `None`

        """
        reference = subject_identifier.to_external_form()
        try:
            topic = self.topic_constructs.get(
                subject_identifiers__address=reference)
        except Topic.DoesNotExist:
            topic = None
        return topic

    def get_topic_by_subject_locator (self, subject_locator):
        """Returns a topic by its subject locator.

        If no topic with the specified subject locator exists, this
        method returns `None`.

        :param subject_locator: the subject locator of the topic to be
          returned
        :type subject_locator: `Locator`
        :rtype: `Topic` of `None`

        """
        reference = subject_locator.to_external_form()
        try:
            topic = self.topic_constructs.get(
                subject_locators__address=reference)
        except Topic.DoesNotExist:
            topic = None
        return topic
    
    def get_topic_map (self):
        """Returns self.

        :rtype: `TopicMap`

        """
        return self

    def remove (self):
        self.delete()

    