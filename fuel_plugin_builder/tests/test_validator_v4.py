# def test_check_compatibility_failed(self):
#     fuel_version_checks = (
#         ['6.0', '6.1', '7.0', '8.0', '9.0'],
#         ['6.0', '6.1', '7.0', '8.0'],
#         ['6.1', '7.0', '8.0']
#     )
#
#     for metadata_fuel_versions in fuel_version_checks:
#         self.data_tree.update(
#             self._make_fake_metadata_data(
#                 fuel_version=metadata_fuel_versions,
#                 package_version=self.ValidatorClass.package_version
#             )
#         )
#
#         report = self.validator.validate(self.data_tree)
#         print report.render()
#         self.assertTrue(report.count_failures() > 0)
#         self.assertIn(
#             u'Current plugin format {package_version} is not compatible '
#             u'with following Fuel versions: {metadata_fuel_versions}\n'
#             u'Fuel version must be {minimal_fuel_version} or higher. '
#             u'Please remove {metadata_fuel_versions} version from '
#             u'{metadata_path} file or downgrade package_version.'.format(
#                 package_version=self.validator.package_version,
#                 minimal_fuel_version=self.validator.minimal_fuel_version,
#                 metadata_fuel_versions=u", ".join(metadata_fuel_versions),
#                 metadata_path='metadata.yaml'
#             ),
#             report.render()
#         )
#
#
# def test_check_compatibility_passed(self):
#     fuel_version_checks = (
#         (['8.0', '9.0', '9.1']),
#         (['8.0', '9.0', '9.1', '9.2']),
#         (['8.0', '9.0', '9.1', '9.2', '10.0']),
#     )
#
#     for fuel_version in fuel_version_checks:
#         metadata = self._make_fake_metadata_data(
#             fuel_version=fuel_version,
#             package_version=self.ValidatorClass.package_version)
#         self.data_tree.update(metadata)
#
#         report = self.validator.validate(self.data_tree)
#         self.assertIn('Validation successful', report.render())
#         self.assertEqual(report.count_failures(), 0)