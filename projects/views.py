from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Organization, Project, ProjectMember, ProjectComment
from .forms import ProjectForm, ProjectMemberForm
from notifications.utils import (
    notify_project_member_added, notify_project_comment, notify_project_created,
    notify_project_updated, log_project_activity
)


class EnterpriseRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only Enterprise users can access"""
    def test_func(self):
        return self.request.user.profile.role == 'ENTERPRISE'


class ProjectListView(LoginRequiredMixin, ListView):
    """List all projects for the user's organization"""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        user = self.request.user
        organization = user.profile.organization
        
        if user.profile.role == 'ENTERPRISE':
            # Enterprise sees all projects in their organization
            return Project.objects.filter(organization=organization)
        elif user.profile.role == 'MANAGER':
            # Manager sees projects they manage
            return Project.objects.filter(manager=user)
        else:
            # Employee sees projects they're a member of
            return Project.objects.filter(members__user=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enterprise'] = self.request.user.profile.role == 'ENTERPRISE'
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """View project details"""
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        user = self.request.user
        organization = user.profile.organization
        return Project.objects.filter(organization=organization)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enterprise'] = self.request.user.profile.role == 'ENTERPRISE'
        context['is_manager'] = self.request.user.profile.role == 'MANAGER'
        context['team_members'] = self.object.members.select_related('user')
        context['tasks'] = self.object.tasks.all()
        context['comments'] = self.object.comments.select_related('user').order_by('-created_at')
        
        # Form to add new team members (only for enterprise)
        if self.request.user.profile.role == 'ENTERPRISE':
            context['member_form'] = ProjectMemberForm(
                organization=self.request.user.profile.organization,
                project=self.object
            )
        return context


class ProjectCreateView(LoginRequiredMixin, EnterpriseRequiredMixin, CreateView):
    """Create a new project"""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.user.profile.organization
        return kwargs
    
    def form_valid(self, form):
        form.instance.organization = self.request.user.profile.organization
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Log activity
        log_project_activity(
            self.object, self.request.user, 'CREATE',
            f'created project "{self.object.name}"'
        )
        
        # Notify other enterprise users about new project
        notify_project_created(self.object, self.request.user)
        
        messages.success(self.request, f'Project "{form.instance.name}" created successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Project'
        context['button_text'] = 'Create Project'
        return context


class ProjectUpdateView(LoginRequiredMixin, EnterpriseRequiredMixin, UpdateView):
    """Update an existing project"""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def get_queryset(self):
        return Project.objects.filter(organization=self.request.user.profile.organization)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.user.profile.organization
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log activity
        log_project_activity(
            self.object, self.request.user, 'UPDATE',
            f'updated project "{self.object.name}"'
        )
        
        # Notify project manager and creator
        notify_project_updated(self.object, self.request.user)
        
        messages.success(self.request, f'Project "{form.instance.name}" updated successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Project'
        context['button_text'] = 'Save Changes'
        return context


class ProjectDeleteView(LoginRequiredMixin, EnterpriseRequiredMixin, DeleteView):
    """Delete a project"""
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:list')
    
    def get_queryset(self):
        return Project.objects.filter(organization=self.request.user.profile.organization)
    
    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        
        # Log activity before deletion
        log_project_activity(
            project, request.user, 'DELETE',
            f'deleted project "{project.name}"'
        )
        
        messages.success(request, f'Project "{project.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_project_member(request, pk):
    """Add a team member to a project"""
    if request.user.profile.role != 'ENTERPRISE':
        messages.error(request, 'You do not have permission to add team members.')
        return redirect('projects:detail', pk=pk)
    
    project = get_object_or_404(
        Project, 
        pk=pk, 
        organization=request.user.profile.organization
    )
    
    if request.method == 'POST':
        form = ProjectMemberForm(
            request.POST,
            organization=request.user.profile.organization,
            project=project
        )
        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()
            
            # Notify the added user
            notify_project_member_added(project, member.user, request.user)
            
            # Log activity
            log_project_activity(
                project, request.user, 'ASSIGN',
                f'added {member.user.get_full_name() or member.user.username} to project'
            )
            
            messages.success(request, f'{member.user.get_full_name() or member.user.username} added to the project!')
        else:
            messages.error(request, 'Error adding team member. Please try again.')
    
    return redirect('projects:detail', pk=pk)


@login_required
def remove_project_member(request, pk, member_id):
    """Remove a team member from a project"""
    if request.user.profile.role != 'ENTERPRISE':
        messages.error(request, 'You do not have permission to remove team members.')
        return redirect('projects:detail', pk=pk)
    
    project = get_object_or_404(
        Project, 
        pk=pk, 
        organization=request.user.profile.organization
    )
    
    member = get_object_or_404(ProjectMember, pk=member_id, project=project)
    username = member.user.get_full_name() or member.user.username
    member.delete()
    messages.success(request, f'{username} removed from the project!')
    
    return redirect('projects:detail', pk=pk)


@login_required
@require_POST
def add_project_comment(request, pk):
    """Add a comment to a project"""
    project = get_object_or_404(
        Project, 
        pk=pk, 
        organization=request.user.profile.organization
    )
    
    comment_text = request.POST.get('comment', '').strip()
    if comment_text:
        comment = ProjectComment.objects.create(
            project=project,
            user=request.user,
            comment=comment_text
        )
        
        # Notify project members
        notify_project_comment(comment, request.user)
        
        # Log activity
        log_project_activity(
            project, request.user, 'COMMENT',
            f'commented on project "{project.name}"'
        )
        
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Please enter a comment.')
    
    return redirect('projects:detail', pk=pk)