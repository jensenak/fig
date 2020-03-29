Named Fig because that's both a reference to "config" and a kind of tree.

This tool takes input data in the form a "tree" (similar to a filesystem or a dictionary, really) and generates a flat config file that can be sourced by bash.

To test:

    pip3 install -r requirements.txt
    python3 -m pytest


--- NOTES FROM PLANNING ---
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

Some thoughts:

This tool definitely has two components.

- A server agent, meant primarily to fetch values for a running process. 
- A management tool, meant to enable developers to set up configuration.

Server agent:

- Probably should have the ability to start a process
  - Being the parent of a process allows it to pass environment vars
  - It would need to pass signals through (such as SIGTERM, SIGSTOP, SIGHUP)
- Might make sense to have it write files when invoked (maybe as an operating mode)
- Possibly support writes?
  - Could enable a service discovery-like functionality where running services can inform others of changing configuration

Management tool:

- Allows set up of a new namespace (just writes a key somewhere)
- Could maybe support some kind of "template" namespace?
- Could aid in keeping config DRY
  - When the same value is set in multiple places, prompt for a higher level setting?
  - This would probably require a running server, instead of just a cli tool...
  - ... unless it was a command ... " >> tool dedup /my/namespace"
- Probably needs import and export modes
