import time
import inspect
 
# Define the decorator factory
def analyze_replica(plan_id = 0, replica_id=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Filter loaded functions and classes
            loaded_functions = {name: obj for name, obj in globals().items() if inspect.isfunction(obj)}
            loaded_classes = {name: obj for name, obj in globals().items() if inspect.isclass(obj)}
 
            print("Plan id ", plan_id, " Replica id ", replica_id)
            print("Passed function")
            print(inspect.getsource(func))
 
            print("Functions loaded in session:")
            for name, f in loaded_functions.items():
                # Skip the wrapper itself and the decorator function
                if name in ['execution_timer', 'decorator', 'wrapper']:
                    continue
                print(f"- {name}:")
                print(inspect.getsource(f))
 
            print("\nClasses loaded in session:")
            for name, cls in loaded_classes.items():
                print(f"- {name}:")
                print(inspect.getsource(cls))
 
            # Find the
            # Call the original function
            result = func(*args, **kwargs)
            return result  # Return the result of the original function
        return wrapper
    return decorator
 
 
# Example standalone function
def print_something():
    print("PRINTING SOMETHING")
 
def print_some_int(integer= 10):
    print("PRINTING SOMETHING ", integer)
 
# Apply the decorator with a parameter
@analyze_replica(plan_id = 100, replica_id=10110)
def example_function(n):
    time.sleep(n)  # Simulate a delay
    print_something()
    return f"Function ran for {n} seconds."
 
 
# Call the decorated function
print(example_function(2))