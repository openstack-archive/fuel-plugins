# Changelog

## 4.2.0 (2017-01-02)

New package version "4.2.0" includes the following features:

- Added new plugin version with node & nic attributes support

Bugfixes:

- Move Release.mako into v1 template dir
  [LP1655289](https://bugs.launchpad.net/fuel/+bug/1655289)
- Make ubuntu repo similar for all plugin versions
  [LP1650551](https://bugs.launchpad.net/fuel/+bug/1650551)
- Show team and repo badges on `README`
- Remove reboot task from plugin example version "3.0.0"
  [LP1625244](https://bugs.launchpad.net/fuel/+bug/1625244)
- Files with no code must be left completely empty
- Legacy deployment tasks are turned back for plugin example version "3.0.0"
  [LP1625244](https://bugs.launchpad.net/fuel/+bug/1625244)
- `tasks.yaml` was commented for plugin example version "3.0.0"
  [LP1625244](https://bugs.launchpad.net/fuel/+bug/1625244)
- Allow unauthenticated packages in the deployment scripts
  [LP1622506](https://bugs.launchpad.net/fuel/+bug/1622506)
- Allow arrays in 'value' in environment_config.yaml
  [LP1616466](https://bugs.launchpad.net/fuel/+bug/1616466)
- Old `tasks.yaml` content is commented for plugins packages version "4.0.0"
  [LP1619255](https://bugs.launchpad.net/fuel/+bug/1619255)
- Allow possibility to provide rpm `Release` version
  [LP1616929](https://bugs.launchpad.net/fuel/+bug/1616929)
- Rename existing BaseValidator to LegacyBaseValidator
  [LP1534126](https://bugs.launchpad.net/fuel/+bug/1534126)
- Fix a word spell error in `README.rst`
- Support multi versions of package in fuel plugin
  [LP1599896](https://bugs.launchpad.net/fuel/+bug/1599896)

## 4.1.0 (2016-06-29)

Bugfixes:

- `tasks.yaml` is now optional for package version "4.0.0"
  [LP1552248](https://bugs.launchpad.net/fuel/+bug/1552248)
- Fuel Mitaka (9.0) is supported by default in package version "4.0.0"
  [LP1549276](https://bugs.launchpad.net/fuel/+bug/1549276)
- Use more reliable way to check for `fpm` Ruby GEM
  [LP1561069](https://bugs.launchpad.net/fuel/+bug/1561069)
- Add ability for role to conflict with all roles by using `*` sign
  [LP1547590](https://bugs.launchpad.net/fuel/+bug/1547590)
- Do not execute `uninstall.sh` on plugin upgrade
  [LP1564123](https://bugs.launchpad.net/fuel/+bug/1564123)
- Add possiblity to use generators in `environment_config.yaml`
  [LP1557562](https://bugs.launchpad.net/fuel/+bug/1557562)
- Don't put any code to PREUN section if `uninstall.sh` doesn't exist or empty
  [LP1574478](https://bugs.launchpad.net/fuel/+bug/1574478)
- Allow a user to specify any arbitrary string as role name for cross-deps
  [LP1557997](https://bugs.launchpad.net/fuel/+bug/1557997)
- Add deployment tasks v2.1 validation support
  [LP1590389](https://bugs.launchpad.net/fuel/+bug/1590389)

## 4.0.0 (2016-02-26)

New package version "4.0.0" includes the following features:

- New flag `is_hotpluggable` in `metadata.yaml` that allows to install and use
  plugin on previously deployed environments.
- Plugin can specify settings group using "group" field in metadata in
  environment_config.yaml file.
- New group `equipment` added to groups list in `metadata.yaml`.
- New `components.yaml` file that allows to declare new components.

Bugfixes:

- Fix of missing strategy parameter in V3 and V4 deployment tasks
  [LP1522785](https://bugs.launchpad.net/fuel/+bug/1522785)

## 3.0.0 (2014-09-16)

New package version "3.0.0" includes the following features:

- New `node_roles.yaml` file that allows to add new node roles.
- New `volumes.yaml` file that allows to add new volumes and/or define
  "node roles <-> volumes" mapping.
- New `deployment_tasks.yaml` file that allows to declare pre/post- and
  regular deployment tasks for any node role. Unlike `tasks.yaml`, the
  tasks go through global deployment graph and that provides ability
  to execute task at any place during deployment, or overwrite/skip
  already existing ones.
- New `network_roles.yaml` file that allows to add new network roles
  and reserve some VIPs, to be proceed by plugin.

Bugfixes:

- Fix executing of `deploy.sh` deployment script
  [LP1463441](https://bugs.launchpad.net/fuel/+bug/1463441)
- Remove "Origin" field from Ubuntu's `Release` file in order to reduce
  probability of broken apt pinning
  [LP1475665](https://bugs.launchpad.net/fuel/+bug/1475665)

## 2.0.4 (2014-06-23)

- Fix, remove plugin package from previous build
  https://bugs.launchpad.net/fuel/+bug/1464143

## 2.0.3 (2014-06-08)

- New "monitoring" group
  https://bugs.launchpad.net/fuel/+bug/1458592
- Fix, fail build, if there are invalid deb packages for ubuntu repository
  https://bugs.launchpad.net/fuel/+bug/1447981
- Fix dependency package name for newer CentOS
  https://bugs.launchpad.net/fuel/+bug/1455882

## 2.0.2 (2014-05-15)

- Reverted fix for https://bugs.launchpad.net/fuel/+bug/1447981
  because it caused creation of broken ubuntu repository
  https://bugs.launchpad.net/fuel-plugins/+bug/1455130

## 2.0.1 (2014-05-08)

- Fix, fail build, if there are invalid deb packages for ubuntu repository
  https://bugs.launchpad.net/fuel/+bug/1447981
- Fix validation for UI restrictions
  https://bugs.launchpad.net/fuel/+bug/1448147
- Fix packages duplication after plugin build
  https://bugs.launchpad.net/fuel/+bug/1451751
- Fix plugin name validation
  https://bugs.launchpad.net/fuel/+bug/1439760

## 2.0.0 (2014-04-30)

- New package version "2.0.0", which is generated by default
- For plugins with 2.0.0 package version, fpb builds rpm packages
  instead of *.fp archives. It was required for plugins updates
  https://github.com/stackforge/fuel-specs/blob/master/specs/6.1/plugins-security-fixes.rst
- New "reboot" task for 2.0.0 plugins, which can reboot the node
  and wait until reboot process is finished, see more details in the specification
  https://github.com/stackforge/fuel-specs/blob/master/specs/6.1/reboot-task-type-for-plugin-developers.rst
- New required field groups, now you can specify a list of groups
  which your plugin implements, see more details in the specification
  https://github.com/stackforge/fuel-specs/blob/master/specs/6.1/plugin-groups.rst
- New required field authors (for plugins with 2.0.0 package version)
- New required field licenses (for plugins with 2.0.0 package version)
- New required field homepage (for plugins with 2.0.0 package version)
- New parameter "--package-version", to generate the plugins in old
  format (e.g. package version 1.0.0)
- Fixed, plugins with package version 2.0.0, generate Release file
  for Ubuntu repositories
  https://bugs.launchpad.net/fuel/+bug/1435892
- New format of stages for plugins with package version 2.0.0,
  added numerical postfixes
  https://github.com/stackforge/fuel-specs/blob/master/specs/6.1/plugins-deployment-order.rst

## 1.0.2 (2014-12-19)

- Show correct message, if 'timeout' field is not specified for
  task in tasks.yaml
  https://bugs.launchpad.net/fuel/+bug/1396234
- Print error messages to stderr instead of stdout
- Fixed validation for environment_config.yaml file, "attributes"
  field is optional
  https://bugs.launchpad.net/fuel/+bug/1396491
- Improved validation for environment_config.yaml file, added
  required fields for attributes
- Generate file with SHA1 checksums for each file in the plugin
  https://bugs.launchpad.net/fuel/+bug/1403960

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
