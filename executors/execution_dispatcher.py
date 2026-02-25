from .frame_executors import *
from .plate_executor import execute_load_full
def execute_command(state, command):
    """Дирижер исполнителей"""
    action = command['action']
    
    if action == 'add':
        return execute_add(state, command['name'], command['specs'])
    
    elif action == 'edit':
        return execute_edit(state, command['name'], command['wells'], command['new_dilution'])
    
    elif action == 'erase':
        return execute_erase(state, command['name'], command['wells'])
    
    elif action == 'rename':
        return execute_rename(state, command['old_name'], command['new_name'])
    
    elif action == 'delete':
        return execute_delete(state, command['name'])
    
    elif action == 'show':
        return execute_show(state, command['target'], command.get('name'))
    elif action == 'load_full':
        return execute_load_full(state, command['file_path'], command['sheet_name'])
    
    elif action == 'undo':
        return state, "Undo"
    
    
    else:
        raise ValueError(f"Неизвестное действие: {action}")