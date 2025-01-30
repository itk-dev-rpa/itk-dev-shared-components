# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.8.3] - 2024-12-02

### Fixed

- Child folders in Graph are now found, even with more than 10 child folders to go through.

## [2.8.2] - 2024-12-02

### Fixed

- Approving cases when the person is marked as "Afsluttet" now works.

## [2.8.1] - 2024-12-02

### Fixed

- Approve case in eflyt when approving individual people now works.

## [2.8.0] - 2024-10-02

### Added

- misc.cpr_util: Function to get birth date from cpr number.
- kmd_nova.nova_cases: Function to get a case on its uuid.

## [2.7.1] - 2024-09-24

### Fixed

- eFlyt: Will now change tab when adding notes

## [2.7.0] - 2024-09-16

### Added

- Added functionality for approving, checking approval status and noting cases

## [2.6.1] - 2024-09-04

### Fixed

- Fixed column number on case_worker

## [2.6.0] - 2024-09-04

### Added

- Added fields to the eflyt Case dataclass for status, cpr, name, case_worker

### Changed

- eflyt.eflyt_case.change_tab now checks if the tab needs to be changed before doing it.
- Dependenices are now only locked to major versions.
- Changed test for change sap password to use dotenv.

## [2.5.0] - 2024-08-14

### Added

- Added modules for use with the Eflyt / Dedalus / Notus address system.
- misc.file_util: handle_save_dialog.
- misc.cvr_lookup: Look up cvr number.
- misc.address_lookup: Look up addresses.

### Fixed

- Conversion of ÆØÅ to Ae Oe Aa when uploading notes to Nova.

## [2.4.0] - 2024-07-30

### Added

- Caseworker for notes.
- Directions for setting up environment variables for test.
- misc.file_util: Wait for download function.

### Changed

- Changed environmental variables to use an .env file

### Fixed
- Some SAP tests were failing due to a missing value
- Changed department and security units from rules to user control
- Minor doc fixes to get_drive_item.

## [2.3.0] - 2024-07-03

### Added

- Function for getting cases based on CVR from KMD Nova.
- Tests for getting cases based on CVR from KMD Nova.
- Module for accessing site and file endpoints in Microsoft Graph.

### Changed

- Unexpected format on caseworker in Nova cases results in None.
- Minor refactoring to move common HTTP request wrappers for Microsoft Graph into their own file.

## [2.2.0] - 2024-05-08

### Added

- Module for getting and creating journal notes in Nova.
- Tests for journal notes.

## [2.1.1] - 2024-04-10

### Fixed

- Documents in Nova can now have a caseworker assigned.

## [2.1.0] - 2024-04-09

### Added

- smtp_util: For sending emails using the smtp protocol.
- Tests for smtp_util.

## [2.0.0] - 2024-04-03

### Changed

#### KMD Nova

- Department and Caseworker classes added.
- Ability to set security unit, department and caseworker on cases.
- Better tests for cases.

### Fixed

- Security unit not set properly on Nova cases.

## [1.3.1] - 2024-02-21

### Fixed

- Key error when accessing a Nova Task without a caseworker.

## [1.3.0] - 2024-02-20

### Added

- SAP.fmcacov module 
  - Function to dismiss "key-popup" in SAP.
  - Function to reliably open forretningspartners in SAP.
- Test for all of the above.

### Changed

- opret_kundekontakt uses the new SAP.fmcacov module.
- Updated Github actions dependencies.

### Removed

- SAP login using web portal. Wasn't used or maintained.

## [1.2.0] - 2024-02-12

### Added

- misc/cpr_util: Function to get age from cpr number.
- Hooks for KMD Nova cases.
- Hooks for KMD Nova tasks.
- Hooks for KMD Nova documents.
- Hooks for CPR address lookup via KMD Nova API.
- Tests for all of the above.

## [1.1.0] - 2023-11-28

### Changed

- sap.opret_kundekontakt: Function 'opret_kundekontakter' made more stable.
- sap.multi_session: Function 'spawn_session' is no longer hardcoded to 1080p screen size.
- sap.multi_session: Arrange session windows moved to separate function.
- Bunch o' linting.
- run_tests.bat: Dedicated test venv.
- readme: Updated readme.

### Added

- Changelog!
- pylint.yml: Flake8 added.

### Fixed

- sap.multi_session: Critical bug in 'run_batches'.
- tests.sap.login: Change environ 'SAP Login' for later tests.

## [1.0.0] - 2023-11-14

- Initial release

[Unreleased]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/compare/2.8.3...HEAD
[2.8.3]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.8.3
[2.8.2]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.8.2
[2.8.1]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.8.1
[2.8.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.8.0
[2.7.1]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.7.1
[2.7.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.7.0
[2.6.1]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.6.1
[2.6.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.6.0
[2.5.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.5.0
[2.4.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.4.0
[2.3.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.3.0
[2.2.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.2.0
[2.1.1]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.1.1
[2.1.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.1.0
[2.0.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/2.0.0
[1.3.1]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/1.3.1
[1.3.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/1.3.0
[1.2.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/1.2.0
[1.1.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/1.1.0
[1.0.0]: https://github.com/itk-dev-rpa/ITK-dev-shared-components/releases/tag/1.0.0
