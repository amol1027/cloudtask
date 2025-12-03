from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import Task, TaskComment, TaskAttachment, TimeEntry, TaskTemplate
from .forms import TaskForm, TaskCommentForm, TaskStatusUpdateForm
from projects.models import Project
from notifications.utils import (
    notify_task_assigned, notify_task_updated, notify_task_comment,
    notify_task_created, log_task_activity
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only Managers or Enterprise users can access"""
    def test_func(self):
        return self.request.user.profile.role in ['MANAGER', 'ENTERPRISE']


class TaskListView(LoginRequiredMixin, ListView):
    """List all tasks for the user"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        user = self.request.user
        organization = user.profile.organization
        
        if user.profile.role == 'ENTERPRISE':
            # Enterprise sees all tasks in their organization
            return Task.objects.filter(project__organization=organization)
        elif user.profile.role == 'MANAGER':
            # Manager sees tasks in their managed projects
            return Task.objects.filter(project__manager=user)
        else:
            # Employee sees only tasks assigned to them
            return Task.objects.filter(assigned_to=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.profile.role in ['MANAGER', 'ENTERPRISE']
        
        # Task statistics
        tasks = self.get_queryset()
        context['todo_count'] = tasks.filter(status='TODO').count()
        context['in_progress_count'] = tasks.filter(status='IN_PROGRESS').count()
        context['in_review_count'] = tasks.filter(status='IN_REVIEW').count()
        context['done_count'] = tasks.filter(status='DONE').count()
        
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """View task details"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        user = self.request.user
        organization = user.profile.organization
        
        if user.profile.role == 'ENTERPRISE':
            return Task.objects.filter(project__organization=organization)
        elif user.profile.role == 'MANAGER':
            return Task.objects.filter(project__manager=user)
        else:
            return Task.objects.filter(assigned_to=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.profile.role in ['MANAGER', 'ENTERPRISE']
        context['is_assignee'] = self.object.assigned_to == self.request.user
        context['comments'] = self.object.comments.select_related('user').order_by('created_at')
        context['attachments'] = self.object.attachments.select_related('uploaded_by').order_by('-uploaded_at')
        context['comment_form'] = TaskCommentForm()
        context['status_form'] = TaskStatusUpdateForm(initial={'status': self.object.status})
        # Get available tasks for dependencies (same project, excluding self)
        context['available_dependencies'] = Task.objects.filter(
            project=self.object.project
        ).exclude(pk=self.object.pk)
        # Check if task is blocked by incomplete dependencies
        context['is_blocked'] = self.object.depends_on.exclude(status='DONE').exists()
        
        # Time tracking
        context['time_entries'] = self.object.time_entries.select_related('user').order_by('-start_time')[:5]
        context['active_timer'] = TimeEntry.objects.filter(
            task=self.object, 
            user=self.request.user, 
            is_running=True
        ).first()
        
        # Calculate total time
        total_minutes = sum(entry.duration_minutes for entry in self.object.time_entries.all())
        hours = total_minutes // 60
        minutes = total_minutes % 60
        context['total_time_display'] = f"{hours}h {minutes}m"
        
        return context


class TaskCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    """Create a new task"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # Check if project is specified in query params
        project_id = self.request.GET.get('project')
        if project_id:
            try:
                kwargs['project'] = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                pass
        
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Handle file attachments
        files = self.request.FILES.getlist('attachments')
        for uploaded_file in files:
            if uploaded_file.size <= MAX_FILE_SIZE:
                TaskAttachment.objects.create(
                    task=self.object,
                    file=uploaded_file,
                    uploaded_by=self.request.user
                )
                log_task_activity(
                    self.object, self.request.user, 'ATTACH',
                    f'attached "{uploaded_file.name}" to "{self.object.title}"'
                )
        
        # Log activity
        log_task_activity(
            self.object, self.request.user, 'CREATE',
            f'created task "{self.object.title}"'
        )
        
        # Notify project manager and enterprise about new task
        notify_task_created(self.object, self.request.user)
        
        # Notify assignee if assigned
        if self.object.assigned_to:
            notify_task_assigned(self.object, self.request.user)
        
        messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Task'
        context['button_text'] = 'Create Task'
        return context


class TaskUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    """Update an existing task"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'ENTERPRISE':
            return Task.objects.filter(project__organization=user.profile.organization)
        else:
            return Task.objects.filter(project__manager=user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['project'] = self.object.project
        return kwargs
    
    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        old_assignee = self.object.assigned_to
        response = super().form_valid(form)
        
        # Handle file attachments
        files = self.request.FILES.getlist('attachments')
        for uploaded_file in files:
            if uploaded_file.size <= MAX_FILE_SIZE:
                TaskAttachment.objects.create(
                    task=self.object,
                    file=uploaded_file,
                    uploaded_by=self.request.user
                )
                log_task_activity(
                    self.object, self.request.user, 'ATTACH',
                    f'attached "{uploaded_file.name}" to "{self.object.title}"'
                )
        
        # Log activity
        log_task_activity(
            self.object, self.request.user, 'UPDATE',
            f'updated task "{self.object.title}"'
        )
        
        # Notify if assignee changed
        if self.object.assigned_to and self.object.assigned_to != old_assignee:
            notify_task_assigned(self.object, self.request.user)
        
        # Notify about update (except assignee who just got notified)
        notify_task_updated(self.object, self.request.user)
        
        messages.success(self.request, f'Task "{form.instance.title}" updated successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Task'
        context['button_text'] = 'Save Changes'
        return context


class TaskDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    """Delete a task"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'ENTERPRISE':
            return Task.objects.filter(project__organization=user.profile.organization)
        else:
            return Task.objects.filter(project__manager=user)
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        
        # Log activity before deletion
        log_task_activity(
            task, request.user, 'DELETE',
            f'deleted task "{task.title}"'
        )
        
        messages.success(request, f'Task "{task.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    """Add a comment to a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check permission
    user = request.user
    if user.profile.role == 'EMPLOYEE' and task.assigned_to != user:
        messages.error(request, 'You can only comment on tasks assigned to you.')
        return redirect('tasks:detail', pk=pk)
    
    if request.method == 'POST':
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = user
            
            # Update task status if specified
            if comment.status_changed_to:
                old_status = task.status
                task.status = comment.status_changed_to
                task.save()
                
                # Log status change
                log_task_activity(
                    task, user, 'STATUS_CHANGE',
                    f'changed status of "{task.title}"',
                    old_value=dict(Task.STATUS_CHOICES).get(old_status),
                    new_value=dict(Task.STATUS_CHOICES).get(comment.status_changed_to)
                )
            
            comment.save()
            
            # Log comment activity
            log_task_activity(
                task, user, 'COMMENT',
                f'commented on "{task.title}"'
            )
            
            # Notify relevant users
            notify_task_comment(comment, user)
            
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment. Please try again.')
    
    return redirect('tasks:detail', pk=pk)


@login_required
def update_status(request, pk):
    """Quick status update for a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check permission - assignee or manager can update status
    user = request.user
    is_assignee = task.assigned_to == user
    is_manager = user.profile.role in ['MANAGER', 'ENTERPRISE']
    
    if not (is_assignee or is_manager):
        messages.error(request, 'You do not have permission to update this task.')
        return redirect('tasks:detail', pk=pk)
    
    if request.method == 'POST':
        form = TaskStatusUpdateForm(request.POST)
        if form.is_valid():
            old_status = task.status
            new_status = form.cleaned_data['status']
            
            if old_status != new_status:
                task.status = new_status
                task.save()
                
                # Log activity
                log_task_activity(
                    task, user, 'STATUS_CHANGE',
                    f'changed status of "{task.title}"',
                    old_value=dict(Task.STATUS_CHOICES).get(old_status),
                    new_value=dict(Task.STATUS_CHOICES).get(new_status)
                )
                
                # Create a comment for the status change
                comment_text = form.cleaned_data.get('comment', '')
                if not comment_text:
                    comment_text = f'Status changed from {dict(Task.STATUS_CHOICES)[old_status]} to {dict(Task.STATUS_CHOICES)[new_status]}'
                
                TaskComment.objects.create(
                    task=task,
                    user=user,
                    comment=comment_text,
                    status_changed_to=new_status
                )
                
                messages.success(request, f'Task status updated to {dict(Task.STATUS_CHOICES)[new_status]}!')
            else:
                messages.info(request, 'No status change was made.')
    
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def upload_attachment(request, pk):
    """Upload a file attachment to a task"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    # Check permission
    is_assignee = task.assigned_to == user
    is_manager = user.profile.role in ['MANAGER', 'ENTERPRISE']
    
    if not (is_assignee or is_manager):
        messages.error(request, 'You do not have permission to upload files to this task.')
        return redirect('tasks:detail', pk=pk)
    
    if 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        
        # Check file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size must be less than 10MB.')
            return redirect('tasks:detail', pk=pk)
        
        attachment = TaskAttachment.objects.create(
            task=task,
            file=uploaded_file,
            uploaded_by=user
        )
        
        # Log activity
        log_task_activity(
            task, user, 'ATTACH',
            f'uploaded "{attachment.filename}" to "{task.title}"'
        )
        
        messages.success(request, f'File "{attachment.filename}" uploaded successfully!')
    else:
        messages.error(request, 'No file was provided.')
    
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def delete_attachment(request, pk, attachment_id):
    """Delete a file attachment"""
    task = get_object_or_404(Task, pk=pk)
    attachment = get_object_or_404(TaskAttachment, pk=attachment_id, task=task)
    user = request.user
    
    # Check permission - only uploader or manager can delete
    is_uploader = attachment.uploaded_by == user
    is_manager = user.profile.role in ['MANAGER', 'ENTERPRISE']
    
    if not (is_uploader or is_manager):
        messages.error(request, 'You do not have permission to delete this file.')
        return redirect('tasks:detail', pk=pk)
    
    filename = attachment.filename
    attachment.file.delete()  # Delete the actual file
    attachment.delete()
    
    messages.success(request, f'File "{filename}" deleted successfully!')
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def add_dependency(request, pk):
    """Add a dependency to a task"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    # Only managers can add dependencies
    if user.profile.role not in ['MANAGER', 'ENTERPRISE']:
        messages.error(request, 'Only managers can manage task dependencies.')
        return redirect('tasks:detail', pk=pk)
    
    dependency_id = request.POST.get('dependency_id')
    if dependency_id:
        try:
            dependency = Task.objects.get(pk=dependency_id, project=task.project)
            if dependency != task and dependency not in task.depends_on.all():
                task.depends_on.add(dependency)
                messages.success(request, f'Dependency on "{dependency.title}" added.')
                
                log_task_activity(
                    task, user, 'UPDATE',
                    f'added dependency on "{dependency.title}" to "{task.title}"'
                )
            else:
                messages.warning(request, 'This dependency already exists or is invalid.')
        except Task.DoesNotExist:
            messages.error(request, 'Invalid task selected.')
    
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def remove_dependency(request, pk, dependency_id):
    """Remove a dependency from a task"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    # Only managers can remove dependencies
    if user.profile.role not in ['MANAGER', 'ENTERPRISE']:
        messages.error(request, 'Only managers can manage task dependencies.')
        return redirect('tasks:detail', pk=pk)
    
    try:
        dependency = Task.objects.get(pk=dependency_id)
        if dependency in task.depends_on.all():
            task.depends_on.remove(dependency)
            messages.success(request, f'Dependency on "{dependency.title}" removed.')
            
            log_task_activity(
                task, user, 'UPDATE',
                f'removed dependency on "{dependency.title}" from "{task.title}"'
            )
    except Task.DoesNotExist:
        messages.error(request, 'Dependency not found.')
    
    return redirect('tasks:detail', pk=pk)


# ============ KANBAN BOARD ============

@login_required
def kanban_board(request):
    """Kanban board view for tasks"""
    user = request.user
    organization = user.profile.organization
    
    # Get tasks based on role
    if user.profile.role == 'ENTERPRISE':
        tasks = Task.objects.filter(project__organization=organization)
    elif user.profile.role == 'MANAGER':
        tasks = Task.objects.filter(project__manager=user)
    else:
        tasks = Task.objects.filter(assigned_to=user)
    
    # Filter by project if specified
    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)
    
    # Organize tasks by status
    columns = {
        'TODO': tasks.filter(status='TODO').select_related('assigned_to', 'project'),
        'IN_PROGRESS': tasks.filter(status='IN_PROGRESS').select_related('assigned_to', 'project'),
        'IN_REVIEW': tasks.filter(status='IN_REVIEW').select_related('assigned_to', 'project'),
        'DONE': tasks.filter(status='DONE').select_related('assigned_to', 'project'),
    }
    
    # Get projects for filter dropdown
    if user.profile.role == 'ENTERPRISE':
        projects = Project.objects.filter(organization=organization)
    elif user.profile.role == 'MANAGER':
        projects = Project.objects.filter(manager=user)
    else:
        projects = Project.objects.filter(members__user=user)
    
    context = {
        'columns': columns,
        'projects': projects,
        'selected_project': project_id,
        'is_manager': user.profile.role in ['MANAGER', 'ENTERPRISE'],
    }
    
    return render(request, 'tasks/kanban_board.html', context)


@login_required
@require_POST
def update_task_status_ajax(request):
    """AJAX endpoint to update task status (for drag-and-drop)"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')
        
        if new_status not in ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        task = get_object_or_404(Task, pk=task_id)
        user = request.user
        
        # Check permission
        is_assignee = task.assigned_to == user
        is_manager = user.profile.role in ['MANAGER', 'ENTERPRISE']
        
        if not (is_assignee or is_manager):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        old_status = task.status
        if old_status != new_status:
            task.status = new_status
            task.save()
            
            # Log activity
            log_task_activity(
                task, user, 'STATUS_CHANGE',
                f'moved "{task.title}" to {dict(Task.STATUS_CHOICES)[new_status]}',
                old_value=dict(Task.STATUS_CHOICES).get(old_status),
                new_value=dict(Task.STATUS_CHOICES).get(new_status)
            )
        
        return JsonResponse({'success': True, 'new_status': new_status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============ TIME TRACKING ============

@login_required
@require_POST
def start_timer(request, pk):
    """Start a timer for a task"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    # Check if user has an active timer
    active_timer = TimeEntry.objects.filter(user=user, is_running=True).first()
    if active_timer:
        # Stop the previous timer
        active_timer.stop()
        messages.info(request, f'Stopped timer on "{active_timer.task.title}"')
    
    # Create new time entry
    TimeEntry.objects.create(
        task=task,
        user=user,
        start_time=timezone.now(),
        is_running=True,
        description=request.POST.get('description', '')
    )
    
    messages.success(request, f'Timer started for "{task.title}"')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def stop_timer(request, pk):
    """Stop the active timer for a task"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    active_timer = TimeEntry.objects.filter(task=task, user=user, is_running=True).first()
    if active_timer:
        active_timer.stop()
        messages.success(request, f'Timer stopped. Logged {active_timer.duration_display}')
    else:
        messages.warning(request, 'No active timer found.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'duration': active_timer.duration_display if active_timer else '0m'})
    return redirect('tasks:detail', pk=pk)


@login_required
@require_POST
def add_time_entry(request, pk):
    """Manually add a time entry"""
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    
    try:
        hours = int(request.POST.get('hours', 0))
        minutes = int(request.POST.get('minutes', 0))
        description = request.POST.get('description', '')
        
        if hours == 0 and minutes == 0:
            messages.error(request, 'Please enter a valid duration.')
            return redirect('tasks:detail', pk=pk)
        
        duration_minutes = hours * 60 + minutes
        now = timezone.now()
        
        TimeEntry.objects.create(
            task=task,
            user=user,
            start_time=now - timezone.timedelta(minutes=duration_minutes),
            end_time=now,
            duration_minutes=duration_minutes,
            description=description,
            is_running=False
        )
        
        messages.success(request, f'Added {hours}h {minutes}m to "{task.title}"')
    except ValueError:
        messages.error(request, 'Invalid time format.')
    
    return redirect('tasks:detail', pk=pk)


@login_required
def get_active_timer(request):
    """Get the user's active timer (AJAX)"""
    user = request.user
    active_timer = TimeEntry.objects.filter(user=user, is_running=True).select_related('task').first()
    
    if active_timer:
        elapsed = (timezone.now() - active_timer.start_time).total_seconds()
        return JsonResponse({
            'has_timer': True,
            'task_id': active_timer.task.id,
            'task_title': active_timer.task.title,
            'start_time': active_timer.start_time.isoformat(),
            'elapsed_seconds': int(elapsed),
        })
    return JsonResponse({'has_timer': False})


# ============ TASK TEMPLATES ============

class TaskTemplateListView(LoginRequiredMixin, ListView):
    """List all task templates"""
    model = TaskTemplate
    template_name = 'tasks/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return TaskTemplate.objects.filter(
            organization=self.request.user.profile.organization
        )


class TaskTemplateCreateView(LoginRequiredMixin, CreateView):
    """Create a task template"""
    model = TaskTemplate
    template_name = 'tasks/template_form.html'
    fields = ['name', 'description', 'default_title', 'default_description', 'default_priority', 'estimated_hours']
    success_url = reverse_lazy('tasks:template_list')
    
    def form_valid(self, form):
        form.instance.organization = self.request.user.profile.organization
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Template "{form.instance.name}" created!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Template'
        context['button_text'] = 'Create Template'
        return context


class TaskTemplateDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a task template"""
    model = TaskTemplate
    template_name = 'tasks/template_confirm_delete.html'
    success_url = reverse_lazy('tasks:template_list')
    
    def get_queryset(self):
        return TaskTemplate.objects.filter(
            organization=self.request.user.profile.organization
        )
    
    def delete(self, request, *args, **kwargs):
        template = self.get_object()
        messages.success(request, f'Template "{template.name}" deleted!')
        return super().delete(request, *args, **kwargs)


@login_required
def create_task_from_template(request, template_id):
    """Create a task from a template"""
    template = get_object_or_404(
        TaskTemplate, 
        pk=template_id,
        organization=request.user.profile.organization
    )
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = get_object_or_404(Project, pk=project_id)
        
        task = Task.objects.create(
            title=template.default_title,
            description=template.default_description,
            priority=template.default_priority,
            project=project,
            created_by=request.user,
            status='TODO'
        )
        
        log_task_activity(
            task, request.user, 'CREATE',
            f'created task from template "{template.name}"'
        )
        
        messages.success(request, f'Task created from template "{template.name}"!')
        return redirect('tasks:detail', pk=task.pk)
    
    # Get projects for selection
    user = request.user
    if user.profile.role == 'ENTERPRISE':
        projects = Project.objects.filter(organization=user.profile.organization)
    else:
        projects = Project.objects.filter(manager=user)
    
    return render(request, 'tasks/create_from_template.html', {
        'template': template,
        'projects': projects,
    })