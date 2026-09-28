def in_groups(user, group_names):
    return user.is_superuser or user.groups.filter(name__in=group_names).exists()