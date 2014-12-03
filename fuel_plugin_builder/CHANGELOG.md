# Changelog

## 1.0.2 (UNRELEASED)

- Show correct message, if 'timeout' field is not specified for
  task in tasks.yaml
  https://bugs.launchpad.net/fuel/+bug/1396234
- Print error messages to stderr instead of stdout
- Fixed validation for environment_config.yaml file, "attributes"
  field is optional
  https://bugs.launchpad.net/fuel/+bug/1396491
- Improved validation for environment_config.yaml file, added
  required fields for attributes

## 1.0.1 (2014-11-20)

- Show instruction for CentOS if not all requirements are installed
- Fixed bug, deploy.sh doesn't have execution permission
  https://bugs.launchpad.net/fuel/+bug/1392736
- Fixed bug, don't fail validation if environment_config.yaml file has checkbox
  https://bugs.launchpad.net/fuel/+bug/1392807

## 1.0.0 (2014-11-13)

Initial public release

- Plugin create
- Plugin build
- Plugin check
