# Changelog

All notable changes to `pydirectus` will be documented in this file.


## [0.2.x] - 2024-09-22

### Added
 - Session retry support (3 attempts)
 - httpx configurable timeout.
 - get folder by UUID useful when many folders have the same name
 - Folder/subfolder creation
 - main objects exports
 - added `collection.get_all()`

### Fixed
 - Uuid field typing
 - operation duration is now properly in ms
 - fixed `query()` when requesting all fields

## [0.2.0] - 2024-09-21

### Added
- Folder partial handling
- Files handling

### Changed
- Moved from `poetry` to `uv`

## [0.1.0] - 2023-03-05

Intial version

### Added
- Directus connexion
- Collections handling
- Items handling
- Query ORM system
