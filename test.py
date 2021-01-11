import multiprocessing.shared_memory as sm
import shared_memory_list as sml


# Temporary test class that can be run to see shared memory in operation
if __name__ == "__main__":
    shared_memory_list = sm.ShareableList(name=sml.list_name)
    while True:
        print(shared_memory_list[sml.sailboat_position_x])
