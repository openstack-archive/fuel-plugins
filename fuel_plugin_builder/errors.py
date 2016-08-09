#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class FuelPluginException(Exception):
    pass


class ReportedException(FuelPluginException):
    def __init__(self, report):
        self.report = report
        super(ReportedException, self).__init__()

    def __str__(self):
        return self.report.render()


class FuelCannotFindCommandError(FuelPluginException):
    pass


class ExecutedErrorNonZeroExitCode(FuelPluginException):
    pass


class PluginDirectoryExistsError(FuelPluginException):
    pass


class ValidationError(FuelPluginException):
    pass


class TaskFieldError(ValidationError):
    pass


class FileIsEmpty(ValidationError):
    def __init__(self, file_path):
        super(FileIsEmpty, self).__init__(
            "File '{0}' is empty".format(file_path)
        )


class FileDoesNotExist(ValidationError):
    def __init__(self, file_path=None):
        super(FileDoesNotExist, self).__init__(
            "File '{0}' does not exist".format(file_path)
        )


class FilesInPathDoesNotExist(ValidationError):
    pass


class WrongPackageVersionError(FuelPluginException):
    pass


class ReleasesDirectoriesError(FuelPluginException):
    pass


class WrongPluginDirectoryError(FuelPluginException):
    pass


class InspectionConfigurationError(FuelPluginException):
    pass


class InvalidFileFormat(FuelPluginException):
    message = "Invalid file format: {}, supported formats are:"

    def __init__(self, path, supported_formats, *args, **kwargs):
        super(InvalidFileFormat, self).__init__(*args, **kwargs)
        self.message = self.message.format(path, supported_formats.join(', '))


class CantReadFile(FuelPluginException):
    message = "Can't read file: {}"

    def __init__(self, path, *args, **kwargs):
        super(CantReadFile, self).__init__(*args, **kwargs)
        self.message = self.message.format(path)


class InvalidFileExtension(FuelPluginException):
    def __init__(self, extension):
        super(InvalidFileExtension, self).__init__(
            "Invalid file extension: {}".format(extension)
        )


class NoPluginFileFound(FuelPluginException):
    message = "Plugin file not found"

    def __init__(self, message):
        self.message = message


class FailedToLoadPlugin(FuelPluginException):
    message = "Failed to load plugin"
