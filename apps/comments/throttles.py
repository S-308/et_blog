from rest_framework.throttling import UserRateThrottle


class CommentRateThrottle(UserRateThrottle):
    scope = "comment"
