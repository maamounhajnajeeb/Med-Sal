from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model


Users = get_user_model()


class Groups:
    
    # just groups
    def add_group(self, name) -> str:
        group = Group.objects.create(name=name)
        return f"<group created: {group.name}>"
    
    def delete_group(self, name) -> str:
        group = Group.objects.delete(name=name)
        return f"<group deleted: {group.name}>"
    
    def change_name(self, group_name, new_name) -> str:
        group = self.get_group(group_name)
        group.name = new_name
        group.save()
        
        return f"<group with name: {group_name} changed to => :{group.name}>"
    
    def get_group(self, name) -> Group:
        group = Group.objects.get(name=name)
        
        return group
    
    # user with groups
    def add_user_to_group(self, user: Users, group_name: str) -> str:
        user.groups.add(Group.objects.get(name=group_name))
        
        return f"{user} added to group {group_name}"
    
    def delete_user_from_group(self, user: Users, group_name: str) -> str:
        user.groups.delete(Group.objects.get(name=group_name))
        
        return f"{user} deleted from group {group_name}"
    
    def flush_user_groups(self, user: Users) -> str:
        user.groups.clear()
        
        return f"user: {user} groups flushed"
    
    def switch_user_groups(self, user: Users, groups: list[str]) -> str:
        user.groups.set(groups)
        
        return f"user {user} now has these groups: {groups}"
    
    # permissions with groups
    def add_permission_to_group(self, group_name: str, perm_obj: list[Permission]) -> str:
        group = self.get_group(group_name)
        group.permissions.add(*perm_obj)
        
        return f"{group_name} now has the perm: {perm_obj.name}"
    
    def delete_permissions_from_group(self, group_name: str, perm_objs: list[Permission]) -> str:
        group = self.get_group(group_name)
        group.permissions.remove(*perm_objs)
        
        return f"{perm_objs} deleted from group: {group_name}"
    
    def switch_group_permissions(self, group_name: str, perm_objs: list[Permission]) -> str:
        group = self.get_group(group_name)
        group.permissions.set(perm_objs)
        
        return f"{group_name} permissions switched to: {perm_objs}"
    
    def flush_group_permissions(self, group_name: str) -> str:
        group = self.get_group(group_name)
        group.permissions.clear()
        
        return f"{group_name} has now permissions any more"
