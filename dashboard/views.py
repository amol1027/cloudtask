from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """Dashboard index view - routes based on user role"""
    user_role = request.user.profile.role
    
    if user_role == 'MANAGER':
        return render(request, 'dashboard/manager_dashboard.html')
    elif user_role == 'EMPLOYEE':
        return render(request, 'dashboard/employee_dashboard.html')
    else:  # ENTERPRISE
        return render(request, 'dashboard/index.html')

@login_required
def team(request):
    """Team view showing all managers and employees"""
    from accounts.models import UserProfile
    
    # Get all staff members (managers and employees)
    staff_members = UserProfile.objects.filter(
        role__in=['MANAGER', 'EMPLOYEE']
    ).select_related('user').order_by('role', 'user__username')
    
    # Calculate counts
    manager_count = staff_members.filter(role='MANAGER').count()
    employee_count = staff_members.filter(role='EMPLOYEE').count()
    
    context = {
        'staff_members': staff_members,
        'manager_count': manager_count,
        'employee_count': employee_count,
    }
    return render(request, 'dashboard/team.html', context)
