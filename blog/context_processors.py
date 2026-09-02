def notifications(request):
    """Expose the current user's recent notifications to every template
    (used by the bell icon dropdown in base.html)."""

    if not request.user.is_authenticated:
        return {}

    qs = request.user.notifications.select_related("sender", "post")

    return {
        "nav_notifications": qs[:6],
        "unread_notif_count": qs.filter(is_read=False).count(),
    }
