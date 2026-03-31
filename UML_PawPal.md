```mermaid
classDiagram
    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }

    class Category {
        <<enumeration>>
        ACTIVITY
        CARE
        FEEDING
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~String~ special_needs
        +__repr__() String
    }

    class Task {
        +String name
        +int duration_minutes
        +Priority priority
        +Category category
        +Optional~String~ time_of_day
        +is_high_priority() bool
        +__repr__() String
    }

    class Owner {
        +String name
        +int available_minutes
        +List~String~ preferences
        +__repr__() String
    }

    class Scheduler {
        -Pet pet
        -Owner owner
        -List~Task~ tasks
        -List~Task~ plan
        +add_task(Task task) None
        +generate_plan() List~Task~
        +explain_plan() String
    }

    Task --> Priority : uses
    Task --> Category : uses
    Scheduler "1" o-- "1" Pet : manages care for
    Scheduler "1" o-- "1" Owner : schedules on behalf of
    Scheduler "1" o-- "0..*" Task : schedules
```
