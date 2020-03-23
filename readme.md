Temporarily named "Project C"

The goal here is to solve some problems in the configuration space.

Problems:

- There's a lot of redundancy in configuration (same values repeated multiple places)
- Configuration is often outside of version control so changes are untracked
- Lack of clarity when adding new applications or services (what values need to be set)

The solutions may require multiple separate tools.

Possible solutions:

- A hierarchical config resolution tool
  - High level values loaded first (e.g. per environment)
  - More specific values override high level (e.g. per app)
  - Values can reference other locations somehow (e.g. app uses database)
- Versioning tool allows variables to be promoted through environments
  - Two types of variables:
    - longitudinal vars have one value set that gets copied through promotion
    - latitudinal vars have different values per env (but how do you test them!?)
  - Variables reference one another so they can be built of reusable components
  - Suggest compositions based on repeated values?
- Config prompter
  - Prompt users to enter values for a new application?
  - Maybe prompt them to enter values for an existing application that's being updated?

