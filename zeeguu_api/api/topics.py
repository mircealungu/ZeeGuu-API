import flask
import zeeguu
from flask import request
from zeeguu.model import Topic, TopicSubscription, TopicFilter

from .utils.route_wrappers import cross_domain, with_session
from .utils.json_result import json_result
from . import api

session = zeeguu.db.session

SUBSCRIBE_TOPIC = "subscribe_topic"
UNSUBSCRIBE_TOPIC = "unsubscribe_topic"
SUBSCRIBED_TOPICS = "subscribed_topics"
INTERESTING_TOPICS = "interesting_topics"
FILTER_TOPIC = "filter_topic"
UNFILTER_TOPIC = "unfilter_topic"
FILTERED_TOPICS = "filtered_topics"
INTERESTING_FILTERS = "interesting_filters"


# ---------------------------------------------------------------------------
@api.route(f"/{SUBSCRIBE_TOPIC}", methods=("POST",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def subscribe_to_topic_with_id():
    """
    :param: topic_id -- the id of the topic to be subscribed to.
    Subscribe to the topic with the given id

    :return: "OK" in case of success
    """

    topic_id = int(request.form.get('topic_id', ''))

    topic_object = Topic.find_by_id(topic_id)
    TopicSubscription.find_or_create(session, flask.g.user, topic_object)

    return "OK"


# ---------------------------------------------------------------------------
@api.route(f"/{UNSUBSCRIBE_TOPIC}/<topic_id>", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def unsubscribe_from_topic(topic_id):
    """
    A user can unsubscribe from the topic with a given ID
    :return: OK / ERROR
    """

    try:
        to_delete = TopicSubscription.with_topic_id(topic_id, flask.g.user)
        session.delete(to_delete)
        session.commit()
    except Exception as e:
        return "OOPS. FEED AIN'T THERE IT SEEMS (" + str(e) + ")"

    return "OK"


# ---------------------------------------------------------------------------
@api.route(f"/{SUBSCRIBED_TOPICS}", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def get_subscribed_topics():
    """
    A user might be subscribed to multiple topics at once.
    This endpoint returns them as a list.

    :return: a json list with feeds for which the user is registered;
     every feed in this list is a dictionary with the following info:
                id = unique id of the topic;
                title = <unicode string>
    """
    subscriptions = TopicSubscription.topics_for_user(flask.g.user)
    topic_list = []
    for sub in subscriptions:
        try:
            topic_list.append(sub.topic.as_dictionary())
        except Exception as e:
            zeeguu.log(str(e))

    return json_result(topic_list)


# ---------------------------------------------------------------------------
@api.route(f"/{INTERESTING_TOPICS}", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def get_interesting_topics():
    """
    Get a list of interesting topics for the given language.
    Interesting topics are for now defined as:
        - The topic is not followed yet
        - The topic is not in the filters list

    :return:
    """
    topic_data = []
    already_filtered = [each.topic for each in TopicFilter.topics_for_user(flask.g.user)]
    already_subscribed = [each.topic for each in TopicSubscription.topics_for_user(flask.g.user)]

    for topic in Topic.get_all_topics():
        if (topic not in already_filtered) and (topic not in already_subscribed):
            topic_data.append(topic.as_dictionary())
    return json_result(topic_data)


# ---------------------------------------------------------------------------
@api.route(f"/{FILTER_TOPIC}", methods=("POST",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def subscribe_to_filter_with_id():
    """
    :param: filter_id -- the id of the filter to be subscribed to.
    Subscribe to the filter with the given id

    :return: "OK" in case of success
    """

    filter_id = int(request.form.get('filter_id', ''))

    filter_object = Topic.find_by_id(filter_id)
    TopicFilter.find_or_create(session, flask.g.user, filter_object)

    return "OK"


# ---------------------------------------------------------------------------
@api.route(f"/{UNFILTER_TOPIC}/<filter_id>", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def unsubscribe_from_filter(filter_id):
    """
    A user can unsubscribe from the filter with a given ID
    :return: OK / ERROR
    """

    try:
        to_delete = TopicFilter.with_topic_id(filter_id, flask.g.user)
        session.delete(to_delete)
        session.commit()
    except Exception as e:
        return "OOPS. FILTER AIN'T THERE IT SEEMS (" + str(e) + ")"

    return "OK"


# ---------------------------------------------------------------------------
@api.route(f"/{FILTERED_TOPICS}", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def get_subscribed_filters():
    """
    A user might be subscribed to multiple filters at once.
    This endpoint returns them as a list.

    :return: a json list with filters for which the user is registered;
     every filter in this list is a dictionary with the following info:
                id = unique id of the topic;
                title = <unicode string>
    """
    filters = TopicFilter.topics_for_user(flask.g.user)
    filter_list = []
    for fil in filters:
        try:
            filter_list.append(fil.topic.as_dictionary())
        except Exception as e:
            zeeguu.log(str(e))

    return json_result(filter_list)


# ---------------------------------------------------------------------------
@api.route(f"/{INTERESTING_FILTERS}", methods=("GET",))
# ---------------------------------------------------------------------------
@cross_domain
@with_session
def get_interesting_filters():
    """
    Get a list of interesting topic filters for the given language.
    Interesting topic filters are for now defined as:
        - The filter is not yet followed
        - The filter is not in the topics list

    :return:
    """
    filter_data = []
    already_filtered = [each.topic for each in TopicFilter.topics_for_user(flask.g.user)]
    already_subscribed = [each.topic for each in TopicSubscription.topics_for_user(flask.g.user)]

    for topic in Topic.get_all_topics():
        if (topic not in already_filtered) and (topic not in already_subscribed):
            filter_data.append(topic.as_dictionary())
    return json_result(filter_data)

