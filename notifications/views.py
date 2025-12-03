from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification, ActivityLog


class NotificationListView(LoginRequiredMixin, ListView):
    """List all notifications for the current user"""
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@login_required
@require_POST
def mark_as_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Redirect to the link if available
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """Get the count of unread notifications (for AJAX)"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_recent_notifications(request):
    """Get recent notifications for dropdown (AJAX)"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]
    
    data = [{
        'id': n.id,
        'type': n.notification_type,
        'title': n.title,
        'message': n.message[:100],
        'link': n.link,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%b %d, %H:%M')
    } for n in notifications]
    
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    return JsonResponse({'notifications': data, 'unread_count': unread_count})


class ActivityLogView(LoginRequiredMixin, ListView):
    """View activity log for the organization"""
    model = ActivityLog
    template_name = 'notifications/activity_log.html'
    context_object_name = 'activities'
    paginate_by = 50
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.organization:
            return ActivityLog.objects.filter(organization_id=user.profile.organization.id)
        return ActivityLog.objects.none()
